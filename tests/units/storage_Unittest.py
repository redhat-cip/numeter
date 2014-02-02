#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import unittest2 as unittest
import os
import sys
import time
import socket
import whisper
import mock
import logging
import json

myPath = os.path.abspath(os.path.dirname(__file__))

#from numeter.storage import Storage
import numeter.storage
#from numeter.redis import RedisConnect

import base as test_base
from test_utils import FakeRedis

_logger = logging.getLogger()
fh = logging.FileHandler("/dev/null")
fh.setLevel(logging.CRITICAL)
_logger.addHandler(fh)

class StorageTestCase(test_base.TestCase):

    def setUp(self):
        super(StorageTestCase, self).setUp()
        self.getgloballog_orig = numeter.storage.Storage.getgloballog
        numeter.storage.Storage.getgloballog = mock.MagicMock()
        self.storage = numeter.storage.Storage(myPath+"/storage_unittest.cfg")
        self.storage._logger = _logger
        self.storage._redis_connexion = FakeRedis()

    def tearDown(self):
        super(StorageTestCase, self).tearDown()
        numeter.storage.Storage.getgloballog = numeter.storage.Storage.getgloballog

    def test_storage_get_host_list(self):
        with mock.patch('__builtin__.open', mock.mock_open(), create=True) as file_mock:
            # Test with Empty file
            file_mock.return_value.readlines.return_value = []
            self.storage._get_host_list()
            self.assertEqual(self.storage._host_list, [])
            # Empty line
            file_mock.return_value.readlines.return_value = ['','']
            self.storage._get_host_list()
            self.assertEqual(self.storage._host_list, [])
            # Test with 3 hostname and one db and password
            file_mock.return_value.readlines.return_value = ['foo','bar']
            self.storage._get_host_list()
            self.assertEqual(self.storage._host_list, ['foo', 'bar',])
            # One host + comment
            file_mock.return_value.readlines.return_value = ['# my host','foo']
            self.storage._get_host_list()
            self.assertEqual(self.storage._host_list, ['foo'])
            # clear \s after hostname
            file_mock.return_value.readlines.return_value = ['foo   ']
            self.storage._get_host_list()
            self.assertEqual(self.storage._host_list, ['foo'])

    def test_storage_paramsVerification(self):
        # 0 host in list must return false
        self.storage._host_listNumber = 0
        self.assertFalse(self.storage.paramsVerification())
        # 1 host in list must return true
        self.storage._host_listNumber = 1
        self.assertTrue(self.storage.paramsVerification())

    def test_storage_get_hostIDHash(self):
        # No cache in redis, generate new hash and write it in redis
        result = self.storage._redis_connexion.get_and_flush_hset()
        self.assertEqual(result, {})
        self.storage._wsp_path_md5_char = 3
        result = self.storage._get_hostIDHash('foo')
        self.assertEqual(result, 'acb')
        result = self.storage._redis_connexion.get_and_flush_hset()
        self.assertEqual(result, {'HOST_ID': {'foo': 'acb'}})
        # Try char = 2
        self.storage._wsp_path_md5_char = 2
        result = self.storage._get_hostIDHash('foo')
        self.assertEqual(result, 'ac')
        result = self.storage._redis_connexion.get_and_flush_hset()
        self.assertEqual(result, {'HOST_ID': {'foo': 'ac'}})
        # Get hash already in redis
        self.storage._redis_connexion.redis_hset("HOST_ID", 'foo', 'bla')
        result = self.storage._get_hostIDHash('foo')
        self.assertEqual(result, 'bla')

    def test_storage_write_info(self):
        # Nan json info
        result = self.storage._write_info('foo', 'This is not json')
        self.assertFalse(result)
        # Empty info
        info_json = json.dumps({})
        result = self.storage._write_info('foo', info_json)
        self.assertFalse(result)
        # MyInfo plugin with no ID or Name
        info_json = json.dumps({'Plugin': 'MyInfo'})
        result = self.storage._write_info('foo', info_json)
        self.assertFalse(result)
        ## MyInfo valid -> generate host HASH and HOSTS in redis and WSP Path
        self.storage._wsp_path_md5_char = 2
        info_json = json.dumps({'Plugin': 'MyInfo','Name': "bar", 'ID': 'foo'})
        result = self.storage._write_info('foo', info_json)
        self.assertTrue(result)
        excepted = {
                    'HOST_ID': {'foo': 'ac'},
                    'WSP_PATH': {'foo': '/opt/numeter/wsp/ac/foo'},
                    'HOSTS': {
                        'foo': {"Plugin": "MyInfo", "hostIDHash": "ac",'' "ID": "foo", "HostIDFiltredName": "foo", "Name": "bar"}
                        }
                    }
        result = self.storage._redis_connexion.get_and_flush_hset()
        self.assertEqual(result['HOST_ID'], excepted['HOST_ID'])
        self.assertEqual(result['WSP_PATH'], excepted['WSP_PATH'])
        self.assertEqual(json.loads(result['HOSTS']['foo']), excepted['HOSTS']['foo'])
        ## Info with no Infos
        info_json = json.dumps({'Plugin': 'foo'})
        result = self.storage._write_info('foo', info_json)
        self.assertFalse(result)
        ## Info just write INFOS in redis
        info_json = json.dumps({'Plugin': 'foo', 'Infos': { 'bar': 'somethings'}})
        result = self.storage._write_info('foo', info_json)
        self.assertTrue(result)
        excepted = {'INFOS@foo': {u'foo': {"Infos": {"bar": "somethings"}, "Plugin": "foo"}}}
        result = self.storage._redis_connexion.get_and_flush_hset()
        self.assertEqual(json.loads(result['INFOS@foo']['foo']), excepted['INFOS@foo']['foo'])

    def test_storage_write_data(self):
        # No WSP_PATH in info
        data_json = json.dumps({})
        result = self.storage._write_data('foo', 'cpu', data_json)
        self.assertFalse(result)
        # Give RRD path for the next checks
        self.storage._redis_connexion.redis_hset("WSP_PATH", 'foo', '/tmp/bla')
        # no data -> true just do nothing
        data_json = json.dumps({})
        result = self.storage._write_data('foo', 'cpu', data_json)
        self.assertTrue(result)
        # Writa new wsp and create dir
        with mock.patch('os.path.exists', mock.MagicMock()) as exists_mock, \
             mock.patch('os.path.isfile', mock.MagicMock()) as isfile_mock, \
             mock.patch('os.makedirs', mock.MagicMock()) as makedirs_mock, \
             mock.patch('whisper.update', mock.MagicMock()) as wsp_update_mock, \
             mock.patch('whisper.create', mock.MagicMock()) as wsp_create_mock:
          isfile_mock.return_value = False
          exists_mock.return_value = False
          data_json = json.dumps({'TimeStamp': '1000000002', 'Values': {'bla': 42}})
          result = self.storage._write_data('foo', 'cpu', data_json)
          self.assertTrue(result)
          makedirs_mock.assert_called_with('/tmp/bla/cpu')
          wsp_create_mock.assert_called_with('/tmp/bla/cpu/bla.wsp',
                        [(60, 1440), (300, 2016), (600, 4608), (3600, 8784)])
          wsp_update_mock.assert_called_with('/tmp/bla/cpu/bla.wsp', '42', '1000000002')

        # Writa new wsp file
        with mock.patch('os.path.exists', mock.MagicMock()) as exists_mock, \
             mock.patch('os.path.isfile', mock.MagicMock()) as isfile_mock, \
             mock.patch('os.makedirs', mock.MagicMock()) as makedirs_mock, \
             mock.patch('whisper.update', mock.MagicMock()) as wsp_update_mock, \
             mock.patch('whisper.create', mock.MagicMock()) as wsp_create_mock:
          isfile_mock.return_value = False
          exists_mock.return_value = True
          data_json = json.dumps({'TimeStamp': '1000000001', 'Values': {'bla': 42}})
          result = self.storage._write_data('foo', 'cpu', data_json)
          self.assertTrue(result)
          wsp_create_mock.assert_called_with('/tmp/bla/cpu/bla.wsp',
                        [(60, 1440), (300, 2016), (600, 4608), (3600, 8784)])
          wsp_update_mock.assert_called_with('/tmp/bla/cpu/bla.wsp', '42', '1000000001')
        ## Update wsp file
        with mock.patch('os.path.exists', mock.MagicMock()) as exists_mock, \
             mock.patch('os.path.isfile', mock.MagicMock()) as isfile_mock, \
             mock.patch('os.makedirs', mock.MagicMock()) as makedirs_mock, \
             mock.patch('whisper.update', mock.MagicMock()) as wsp_update_mock, \
             mock.patch('whisper.create', mock.MagicMock()) as wsp_create_mock:
          isfile_mock.return_value = True
          data_json = json.dumps({'TimeStamp': '1000000000', 'Values': {'bla': 42}})
          result = self.storage._write_data('foo', 'cpu', data_json)
          self.assertTrue(result)
          wsp_update_mock.assert_called_with('/tmp/bla/cpu/bla.wsp', '42', '1000000000')
