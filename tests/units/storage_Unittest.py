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
        #result = self.storage._redis_connexion.get_and_flush_hset()
        #result = self.storage._write_info( hostID, info_json)
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
                        'foo': '{"Plugin": "MyInfo", "hostIDHash": "ac",'' "ID": "foo", "HostIDFiltredName": "foo", "Name": "bar"}'
                        }
                    }
        result = self.storage._redis_connexion.get_and_flush_hset()
        self.assertEqual(result, excepted)
        ## Info with no Infos
        info_json = json.dumps({'Plugin': 'foo'})
        result = self.storage._write_info('foo', info_json)
        self.assertFalse(result)
        ## Info just write INFOS in redis
        info_json = json.dumps({'Plugin': 'foo', 'Infos': { 'bar': 'somethings'}})
        result = self.storage._write_info('foo', info_json)
        self.assertTrue(result)
        excepted = {'INFOS@foo': {u'foo': '{"Infos": {"bar": "somethings"}, "Plugin": "foo"}'}}
        result = self.storage._redis_connexion.get_and_flush_hset()
        self.assertEqual(result, excepted)

    def test_storage_write_data(self):
        pass

#    def test_storage_getData(self):
#        # Start connexion storage (db2)
#        self.storage._redis_storage_db = 2
#        storageRedis = self.storage.redisStartConnexion()
#        # Start connexion client (db1)
#        self.storage._redis_storage_db = 1
#        collectorRedis = self.storage.redisStartConnexion()
#        # no data
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        (allTS,hostDatas) = self.storage.getData(collectorRedis,'myhost')
#        self.assertEqual((allTS,hostDatas), ([], {}))
#        # One TS but no datas (clean TS)
#        collectorRedis.redis_zadd("TS@myhost",'1000000000',1000000000)
#        (allTS,hostDatas) = self.storage.getData(collectorRedis,'myhost')
#        self.assertEqual((allTS,hostDatas), ([], {}))
#        result = collectorRedis.redis_zrangebyscore("TS@myhost",'-inf','+inf')
#        self.assertEqual(result, [])
#        # Fetch data and delete older data with no TS
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        collectorRedis.redis_zadd("TS@myhost",'1000000001',1000000001)
#        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000000","Values":{"old": "0"}}',1000000000)
#        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000001","Values":{"new": "0"}}',1000000001)
#        (allTS,hostDatas) = self.storage.getData(collectorRedis,'myhost')
#        self.assertEqual((allTS,hostDatas), (['1000000001'], {u'foo': {u'1000000001': {u'new': u'0'}}}))
#        result = collectorRedis.redis_zrangebyscore("DATAS@myhost",'-inf','+inf')
#        self.assertEqual(result, ['{"Plugin":"foo","TimeStamp":"1000000001","Values":{"new": "0"}}']) # Clean old datas
#        # Dont fetch or delete new data without TS + clean old without ts
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        collectorRedis.redis_zadd("TS@myhost",'1000000001',1000000001)
#        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000000","Values":{"old": "0"}}',1000000000)
#        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000001","Values":{"curr": "0"}}',1000000001)
#        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000002","Values":{"new": "0"}}',1000000002)
#        (allTS,hostDatas) = self.storage.getData(collectorRedis,'myhost')
#        self.assertEqual((allTS,hostDatas), (['1000000001'], {u'foo': {u'1000000001': {u'curr': u'0'}}}))
#        result = collectorRedis.redis_zrangebyscore("DATAS@myhost",'-inf','+inf')
#        self.assertEqual(result, ['{"Plugin":"foo","TimeStamp":"1000000001","Values":{"curr": "0"}}',
#                                  '{"Plugin":"foo","TimeStamp":"1000000002","Values":{"new": "0"}}']) # Clean old datas
#        # Fetch bad data and dont stock them
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        collectorRedis.redis_zadd("TS@myhost",'1000000001',1000000001)
#        collectorRedis.redis_zadd("TS@myhost",'1000000002',1000000002)
#        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000001","Values":{"curr": "0"}}',1000000001)
#        collectorRedis.redis_zadd("DATAS@myhost",'{"Values":{"new": "0"}}',1000000002)
#        (allTS,hostDatas) = self.storage.getData(collectorRedis,'myhost')
#        self.assertEqual((allTS,hostDatas), (['1000000001', '1000000002'], {u'foo': {u'1000000001': {u'curr': u'0'}}}))
#        result = collectorRedis.redis_zrangebyscore("DATAS@myhost",'-inf','+inf')
#        self.assertEqual(result, ['{"Plugin":"foo","TimeStamp":"1000000001","Values":{"curr": "0"}}',
#                                  '{"Values":{"new": "0"}}'])
#        # 2 data dispo and max_data_by_hosts are 1, so dont get value 2
#        self.storage._max_data_by_hosts = 1
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        collectorRedis.redis_zadd("TS@myhost",'1000000001',1000000001)
#        collectorRedis.redis_zadd("TS@myhost",'1000000002',1000000002)
#        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000001","Values":{"curr": "0"}}',1000000001)
#        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000002","Values":{"new": "0"}}',1000000002)
#        (allTS,hostDatas) = self.storage.getData(collectorRedis,'myhost')
#        self.assertEqual((allTS,hostDatas), (['1000000001'], {u'foo': {u'1000000001': {u'curr': u'0'}}}))
#        result = collectorRedis.redis_zrangebyscore("DATAS@myhost",'-inf','+inf')
#        self.assertEqual(result, ['{"Plugin":"foo","TimeStamp":"1000000001","Values":{"curr": "0"}}',
#                                  '{"Plugin":"foo","TimeStamp":"1000000002","Values":{"new": "0"}}'])
#

#    def test_storage_getInfos(self):
#        # Start connexion storage (db2)
#        self.storage._redis_storage_db = 2
#        storageRedis = self.storage.redisStartConnexion()
#        self.storage._redis_connexion = storageRedis
#        self.storage._rrd_path_md5_char = 2
#        # Start connexion client (db1)
#        self.storage._redis_storage_db = 1
#        collectorRedis = self.storage.redisStartConnexion()
#        # No Infos
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        (writedinfo, result, rrdPath) = self.storage.getInfos(collectorRedis,'myhost')
#        self.assertEqual(result, {})
#        self.assertEqual(writedinfo, [])
#        # One good info + MyInfo
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        foo = '{"Plugin": "foo", "Infos": { "bar":{"id": "bar"}, "gnu":{"type": "COUNTER", "id": "gnu"}}}'
#        MyInfo = '{ "Plugin": "MyInfo", "ID": "myhost", "Name": "myhostName"}'
#        collectorRedis.redis_hset("INFOS@myhost","foo",foo)
#        collectorRedis.redis_hset("INFOS@myhost","MyInfo",MyInfo)
#        (writedinfo, result, rrdPath) = self.storage.getInfos(collectorRedis,'myhost')
#        self.assertEqual(result, {'MyInfo': {u'Name': u'myhostName', 'HostIDHash': 'cc', u'ID': u'myhost', 'HostIDFiltredName': u'myhost', u'Plugin': u'MyInfo'}, 'foo': {u'Infos': {u'bar': {u'id': u'bar'}, u'gnu': {u'type': u'COUNTER', u'id': u'gnu'}}, u'Plugin': u'foo'}} )
#        self.assertEqual(writedinfo, ['foo', 'MyInfo'])
#        # Only myinfo.
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        MyInfo = '{ "Plugin": "MyInfo", "ID": "myhost", "Name": "myhostName"}'
#        collectorRedis.redis_hset("INFOS@myhost","MyInfo",MyInfo)
#        (writedinfo, result, rrdPath) = self.storage.getInfos(collectorRedis,'myhost')
#        self.assertEqual(result, {'MyInfo': {u'Name': u'myhostName', 'HostIDHash': 'cc', u'ID': u'myhost', 'HostIDFiltredName': u'myhost', u'Plugin': u'MyInfo'}} )
#        # Plugin with no Infos so return only MyInfo
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        MyInfo = '{ "Plugin": "MyInfo", "ID": "myhost", "Name": "myhostName"}'
#        foo = '{"Plugin": "foo"}'
#        collectorRedis.redis_hset("INFOS@myhost","foo",foo)
#        collectorRedis.redis_hset("INFOS@myhost","MyInfo",MyInfo)
#        (writedinfo, result, rrdPath) = self.storage.getInfos(collectorRedis,'myhost')
#        self.assertEqual(result, {'MyInfo': {u'Name': u'myhostName', 'HostIDHash': 'cc', u'ID': u'myhost', 'HostIDFiltredName': u'myhost', u'Plugin': u'MyInfo'}} )
#        self.assertEqual(writedinfo, ['MyInfo'])
#        # No MyInfo so return {} (can't write rrd)
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        foo = '{"Plugin": "foo", "Infos": {}}'
#        collectorRedis.redis_hset("INFOS@myhost","foo",foo)
#        (writedinfo, result, rrdPath) = self.storage.getInfos(collectorRedis,'myhost')
#        self.assertEqual(result, {} )
#        self.assertEqual(writedinfo, [])
#        # Test hostid name filter
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        MyInfo = '{"Name": "myhostName", "Plugin": "MyInfo", "ID": "myhost"}'
#        collectorRedis.redis_hset("INFOS@myhost","MyInfo",MyInfo)
#        (writedinfo, result, rrdPath) = self.storage.getInfos(collectorRedis,'myhost')
#        self.assertEqual(result["MyInfo"]["HostIDFiltredName"], "myhost" )
#        MyInfo = '{"Name": "myhostName", "Plugin": "MyInfo", "ID": "my\'host"}'
#        collectorRedis.redis_hset("INFOS@myhost","MyInfo",MyInfo)
#        (writedinfo, result, rrdPath) = self.storage.getInfos(collectorRedis,'myhost')
#        self.assertEqual(result["MyInfo"]["HostIDFiltredName"], "myhost" )
#        MyInfo = '{ "Plugin": "MyInfo", "ID": "Foo bar", "Name": "myhostName"}'
#        collectorRedis.redis_hset("INFOS@myhost","MyInfo",MyInfo)
#        (writedinfo, result, rrdPath) = self.storage.getInfos(collectorRedis,'myhost')
#        self.assertEqual(result["MyInfo"]["HostIDFiltredName"], "Foobar" )
#        MyInfo = '{ "Plugin": "MyInfo", "ID": "Foo\\"bar", "Name": "myhostName"}'
#        collectorRedis.redis_hset("INFOS@myhost","MyInfo",MyInfo)
#        (writedinfo, result, rrdPath) = self.storage.getInfos(collectorRedis,'myhost')
#        self.assertEqual(result["MyInfo"]["HostIDFiltredName"], "Foobar" )
#        # Test md5 sum
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        self.storage._rrd_path_md5_char = 32
#        MyInfo = '{ "Plugin": "MyInfo", "ID": "foobar", "Name": "myhostName"}'
#        collectorRedis.redis_hset("INFOS@myhost","MyInfo",MyInfo)
#        (writedinfo, result, rrdPath) = self.storage.getInfos(collectorRedis,'myhost')
#        self.assertEqual(result["MyInfo"]["HostIDHash"], "3858f62230ac3c915f300c664312c63f" )
#        # Test md5 rrd_path_md5_char
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        self.storage._rrd_path_md5_char = 5
#        MyInfo = '{ "Plugin": "MyInfo", "ID": "foobar", "Name": "myhostName"}'
#        collectorRedis.redis_hset("INFOS@myhost","MyInfo",MyInfo)
#        (writedinfo, result, rrdPath) = self.storage.getInfos(collectorRedis,'myhost')
#        self.assertEqual(result["MyInfo"]["HostIDHash"], "3858f" )
#        #
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        self.storage._rrd_path_md5_char = 2
#        MyInfo = '{ "Plugin": "MyInfo", "ID": "foobar", "Name": "myhostName"}'
#        collectorRedis.redis_hset("INFOS@myhost","MyInfo",MyInfo)
#        (writedinfo, result, rrdPath) = self.storage.getInfos(collectorRedis,'myhost')
#        self.assertEqual(result["MyInfo"]["HostIDHash"], "38" )
#        # Try to read in cache
#        result = storageRedis.redis_hset("HOST_ID","foobar","42")
#        (writedinfo, result, rrdPath) = self.storage.getInfos(collectorRedis,'myhost')
#        self.assertEqual(result["MyInfo"]["HostIDHash"], "42")
#        # Test rrd path fot host
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        self.storage._rrd_path_md5_char = 2
#        MyInfo = '{ "Plugin": "MyInfo", "ID": "myhost", "Name": "myhostName"}'
#        collectorRedis.redis_hset("INFOS@myhost","MyInfo",MyInfo)
#        self.storage.getInfos(collectorRedis,'myhost')
#        result = storageRedis.redis_hget("RRD_PATH","myhost")
#        self.assertEqual(result, "/tmp/numeter_rrds/cc/myhost")
#        # Test filtred name
#        MyInfo = '{ "Plugin": "MyInfo", "ID": "foo bar", "Name": "myhostName"}'
#        collectorRedis.redis_hset("INFOS@foo bar","MyInfo",MyInfo)
#        self.storage.getInfos(collectorRedis,'foo bar')
#        result = storageRedis.redis_hget("RRD_PATH","foo bar")
#        self.assertEqual(result, "/tmp/numeter_rrds/32/foobar")
#        # Test rrd path fot host
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        self.storage._rrd_path_md5_char = 2
#        MyInfo = '{ "Plugin": "MyInfo", "ID": "foo", "Name": "myhostName"}'
#        collectorRedis.redis_hset("INFOS@foo","MyInfo",MyInfo)
#        self.storage.getInfos(collectorRedis,'foo')
#        result = storageRedis.redis_hget("HOSTS","foo")
#        self.assertEqual(result, '{"Name": "myhostName", "HostIDHash": "ac", "ID": "foo", "HostIDFiltredName": "foo", "Plugin": "MyInfo"}')
#
#
#    def test_sorage_cleanInfo(self):
#        # Start connexion storage (db2)
#        self.storage._redis_storage_db = 2
#        storageRedis = self.storage.redisStartConnexion()
#        self.storage._redis_connexion = storageRedis
#        self.storage._rrd_path_md5_char = 2
#        #
#        # Init delete rrd
#        #
#        self.storage._rrd_delete = True
#        host = 'myhost'
#        rrd_path = '/tmp/rrd_unittest/myhost'
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        os.system("rm -Rf "+rrd_path); os.system("mkdir -p "+rrd_path)
#        # No Infos / no writed
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        writedInfo = []
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hgetall("INFOS@"+host)
#        self.assertEqual(result, {})
#        # No data before
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        writedInfo = ['foo','bar']
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hgetall("INFOS@"+host)
#        self.assertEqual(result, {})
#        # 2 data before and same data now
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        storageRedis.redis_hset("INFOS@"+host,'foo','foo')
#        storageRedis.redis_hset("INFOS@"+host,'bar','bar')
#        writedInfo = ['foo','bar']
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("INFOS@"+host)
#        self.assertEquals(result, ['foo', 'bar'])
#        # 2 data before and only one now
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        os.system("rm -Rf "+rrd_path); os.system("mkdir -p "+rrd_path)
#        os.system("mkdir -p "+rrd_path+'/foo') ; os.system("mkdir -p "+rrd_path+'/bar')
#        storageRedis.redis_hset("INFOS@"+host,'foo','foo')
#        storageRedis.redis_hset("INFOS@"+host,'bar','bar')
#        writedInfo = ['foo']
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("INFOS@"+host)
#        self.assertEquals(result, ['foo'])
#        self.assertFalse(os.path.isdir(rrd_path+'/bar'))
#        self.assertTrue(os.path.isdir(rrd_path+'/foo'))
#        # 2 data before, now 2 new
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        os.system("rm -Rf "+rrd_path); os.system("mkdir -p "+rrd_path)
#        os.system("mkdir -p "+rrd_path+'/foo') ; os.system("mkdir -p "+rrd_path+'/bar')
#        storageRedis.redis_hset("INFOS@"+host,'foo','foo')
#        storageRedis.redis_hset("INFOS@"+host,'bar','bar')
#        writedInfo = ['gnu','bli']
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("INFOS@"+host)
#        self.assertEquals(result, [])
#        self.assertFalse(os.path.isdir(rrd_path+'/bar'))
#        self.assertFalse(os.path.isdir(rrd_path+'/foo'))
#        # 2 data before and old + 2 new now
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        storageRedis.redis_hset("INFOS@"+host,'foo','foo')
#        storageRedis.redis_hset("INFOS@"+host,'bar','bar')
#        writedInfo = ['foo','bar','gnu','bli']
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("INFOS@"+host)
#        self.assertEquals(result, ['foo', 'bar'])
#        # 2 data before. 1 old deleted and one new
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        os.system("rm -Rf "+rrd_path); os.system("mkdir -p "+rrd_path)
#        os.system("mkdir -p "+rrd_path+'/foo') ; os.system("mkdir -p "+rrd_path+'/bar')
#        storageRedis.redis_hset("INFOS@"+host,'foo','foo')
#        storageRedis.redis_hset("INFOS@"+host,'bar','bar')
#        writedInfo = ["foo","gnu"]
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("INFOS@"+host)
#        self.assertEquals(result, ['foo'])
#        self.assertFalse(os.path.isdir(rrd_path+'/bar'))
#        self.assertTrue(os.path.isdir(rrd_path+'/foo'))
#        # 1 data must be erase but bug rrdpath not found so do nothing
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        os.system("rm -Rf "+rrd_path); os.system("mkdir -p "+rrd_path)
#        os.system("mkdir -p "+rrd_path+'/foo')
#        storageRedis.redis_hset("INFOS@"+host,'foo','foo')
#        writedInfo = []
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("INFOS@"+host)
#        self.assertEquals(result, ['foo'])
#        self.assertTrue(os.path.isdir(rrd_path+'/foo'))
#        #
#        # Init delete rrd
#        #
#        self.storage._rrd_delete = False
#        # No Infos / no writed
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        writedInfo = []
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("DELETED_PLUGINS")
#        self.assertEqual(result, [])
#        # No data before (dont delete)
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        writedInfo = ['foo','bar']
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("DELETED_PLUGINS")
#        self.assertEqual(result, [])
#        # 2 data before and same data now
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        storageRedis.redis_hset("INFOS@"+host,'foo','foo')
#        storageRedis.redis_hset("INFOS@"+host,'bar','bar')
#        writedInfo = ['foo','bar']
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("DELETED_PLUGINS")
#        self.assertEquals(result, [])
#        # 2 data before and only one now
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        storageRedis.redis_hset("INFOS@"+host,'foo','foo')
#        storageRedis.redis_hset("INFOS@"+host,'bar','bar')
#        writedInfo = ['foo']
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("DELETED_PLUGINS")
#        self.assertEquals(result, [host+'@bar'])
#        # 2 data before, now 2 new
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        storageRedis.redis_hset("INFOS@"+host,'foo','foo')
#        storageRedis.redis_hset("INFOS@"+host,'bar','bar')
#        writedInfo = ['gnu','bli']
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("DELETED_PLUGINS")
#        self.assertEquals(result, [host+'@foo', host+'@bar'])
#        # 2 data before and old + 2 new now
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        storageRedis.redis_hset("INFOS@"+host,'foo','foo')
#        storageRedis.redis_hset("INFOS@"+host,'bar','bar')
#        writedInfo = ['foo','bar','gnu','bli']
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("DELETED_PLUGINS")
#        self.assertEquals(result, [])
#        # 2 data before. 1 old deleted and one new
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        storageRedis.redis_hset("INFOS@"+host,'foo','foo')
#        storageRedis.redis_hset("INFOS@"+host,'bar','bar')
#        writedInfo = ["foo","gnu"]
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("DELETED_PLUGINS")
#        self.assertEquals(result, [host+'@bar'])
#        # 1 data must be erase but bug rrdpath not found so do nothing
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("INFOS@"+host,'foo','foo')
#        writedInfo = []
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("DELETED_PLUGINS")
#        self.assertEquals(result, [])
#        # 2 datas notify but one reappeared
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("RRD_PATH",host,rrd_path)
#        storageRedis.redis_hset("INFOS@"+host,'foo','foo')
#        storageRedis.redis_hset("DELETED_PLUGINS",host+"@foo","rrdpath")
#        storageRedis.redis_hset("DELETED_PLUGINS",host+"@bar","rrdpath")
#        writedInfo = ["foo"]
#        self.storage.cleanInfo(writedInfo,host)
#        result = storageRedis.redis_hkeys("DELETED_PLUGINS")
#        self.assertEquals(result, [host+'@bar'])
#
#
#    def test_sorage_cleanHosts(self):
#        # Start connexion storage (db2)
#        self.storage._redis_storage_db = 2
#        storageRedis = self.storage.redisStartConnexion()
#        self.storage._redis_connexion = storageRedis
#        self.storage._rrd_path_md5_char = 2
#        #
#        # Init delete rrd
#        #
#        self.storage._rrd_delete = True
#        rrd_path = '/tmp/rrd_unittest'
#        # No Infos / no writed
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        self.storage.cleanHosts([])
#        result = storageRedis.redis_hkeys("HOSTS")
#        self.assertEquals(result, [])
#        result = storageRedis.redis_hkeys("DELETED_HOSTS")
#        self.assertEquals(result, [])
#        # No data before + new datas
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        self.storage.cleanHosts(['foo'])
#        result = storageRedis.redis_hkeys("HOSTS")
#        self.assertEquals(result, [])
#        result = storageRedis.redis_hkeys("DELETED_HOSTS")
#        self.assertEquals(result, [])
#        # 2 data before and same data now
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        os.system("rm -Rf "+rrd_path); os.system("mkdir -p "+rrd_path)
#        storageRedis.redis_hset("HOSTS",'foo',"MyInfo")
#        storageRedis.redis_hset("HOSTS",'bar',"MyInfo")
#        storageRedis.redis_hset("RRD_PATH",'foo',rrd_path+'/foo')
#        storageRedis.redis_hset("RRD_PATH",'bar',rrd_path+'/bar')
#        os.system("mkdir -p "+rrd_path+'/foo')
#        os.system("mkdir -p "+rrd_path+'/bar')
#        self.storage.cleanHosts(['foo','bar'])
#        result = storageRedis.redis_hkeys("HOSTS")
#        self.assertEquals(result, ['foo', 'bar'])
#        self.assertTrue(os.path.isdir(rrd_path+'/bar'))
#        self.assertTrue(os.path.isdir(rrd_path+'/foo'))
#        # 2 data before and only one now
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        os.system("rm -Rf "+rrd_path); os.system("mkdir -p "+rrd_path)
#        storageRedis.redis_hset("INFOS@bar",'plug',"info")
#        storageRedis.redis_hset("INFOS@foo",'plug',"info")
#        storageRedis.redis_hset("HOSTS",'foo',"MyInfo")
#        storageRedis.redis_hset("HOSTS",'bar',"MyInfo")
#        storageRedis.redis_hset("RRD_PATH",'foo',rrd_path+'/foo')
#        storageRedis.redis_hset("RRD_PATH",'bar',rrd_path+'/bar')
#        os.system("mkdir -p "+rrd_path+'/foo')
#        os.system("mkdir -p "+rrd_path+'/bar')
#        self.storage.cleanHosts(['foo'])
#        result = storageRedis.redis_hkeys("HOSTS")
#        self.assertEquals(result, ['foo'])
#        result = storageRedis.redis_hkeys("INFOS@bar")
#        self.assertEquals(result, [])
#        result = storageRedis.redis_hkeys("RRD_PATH")
#        self.assertEquals(result, ['foo'])
#        self.assertFalse(os.path.isdir(rrd_path+'/bar'))
#        self.assertTrue(os.path.isdir(rrd_path+'/foo'))
#        # 2 data before, now 2 new
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        os.system("rm -Rf "+rrd_path); os.system("mkdir -p "+rrd_path)
#        storageRedis.redis_hset("INFOS@bar",'plug',"info")
#        storageRedis.redis_hset("INFOS@foo",'plug',"info")
#        storageRedis.redis_hset("HOSTS",'foo',"MyInfo")
#        storageRedis.redis_hset("HOSTS",'bar',"MyInfo")
#        storageRedis.redis_hset("RRD_PATH",'foo',rrd_path+'/foo')
#        storageRedis.redis_hset("RRD_PATH",'bar',rrd_path+'/bar')
#        os.system("mkdir -p "+rrd_path+'/foo')
#        os.system("mkdir -p "+rrd_path+'/bar')
#        self.storage.cleanHosts(['gnu','bli'])
#        result = storageRedis.redis_hkeys("HOSTS")
#        self.assertEquals(result, [])
#        self.assertFalse(os.path.isdir(rrd_path+'/bar'))
#        self.assertFalse(os.path.isdir(rrd_path+'/foo'))
#        # 2 data before. 1 old deleted and one new
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        os.system("rm -Rf "+rrd_path); os.system("mkdir -p "+rrd_path)
#        storageRedis.redis_hset("INFOS@bar",'plug',"info")
#        storageRedis.redis_hset("INFOS@foo",'plug',"info")
#        storageRedis.redis_hset("HOSTS",'foo',"MyInfo")
#        storageRedis.redis_hset("HOSTS",'bar',"MyInfo")
#        storageRedis.redis_hset("RRD_PATH",'foo',rrd_path+'/foo')
#        storageRedis.redis_hset("RRD_PATH",'bar',rrd_path+'/bar')
#        os.system("mkdir -p "+rrd_path+'/foo')
#        os.system("mkdir -p "+rrd_path+'/bar')
#        self.storage.cleanHosts(['foo','gnu'])
#        result = storageRedis.redis_hkeys("HOSTS")
#        self.assertEquals(result, ['foo'])
#        self.assertFalse(os.path.isdir(rrd_path+'/bar'))
#        self.assertTrue(os.path.isdir(rrd_path+'/foo'))
#        # Must delete 2 host but first have no rrd infos (delete only the last)
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        os.system("rm -Rf "+rrd_path); os.system("mkdir -p "+rrd_path)
#        storageRedis.redis_hset("INFOS@bar",'plug',"info")
#        storageRedis.redis_hset("INFOS@foo",'plug',"info")
#        storageRedis.redis_hset("HOSTS",'foo',"MyInfo")
#        storageRedis.redis_hset("HOSTS",'bar',"MyInfo")
#        storageRedis.redis_hset("RRD_PATH",'bar',rrd_path+'/bar')
#        os.system("mkdir -p "+rrd_path+'/foo')
#        os.system("mkdir -p "+rrd_path+'/bar')
#        self.storage.cleanHosts([])
#        result = storageRedis.redis_hkeys("HOSTS")
#        self.assertEquals(result, ['foo'])
#        self.assertFalse(os.path.isdir(rrd_path+'/bar'))
#        self.assertTrue(os.path.isdir(rrd_path+'/foo'))
#        # 1 data must be erase but bug rrdpath not found so do nothing
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        os.system("rm -Rf "+rrd_path); os.system("mkdir -p "+rrd_path)
#        storageRedis.redis_hset("INFOS@foo",'plug',"info")
#        storageRedis.redis_hset("HOSTS",'foo',"MyInfo")
#        os.system("mkdir -p "+rrd_path+'/foo')
#        self.storage.cleanHosts([])
#        result = storageRedis.redis_hkeys("HOSTS")
#        self.assertEquals(result, ['foo'])
#        self.assertTrue(os.path.isdir(rrd_path+'/foo'))
#        #
#        # Init delete rrd
#        #
#        self.storage._rrd_delete = False
#        # No Infos / no writed
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        writedInfo = []
#        self.storage.cleanHosts([])
#        result = storageRedis.redis_hkeys("DELETED_HOSTS")
#        self.assertEqual(result, [])
#        # No data before + new datas
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        self.storage.cleanHosts(['foo','bar'])
#        result = storageRedis.redis_hkeys("DELETES_HOSTS")
#        self.assertEquals(result, [])
#        # 2 data before and same data now
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("INFOS@bar",'plug',"info")
#        storageRedis.redis_hset("INFOS@foo",'plug',"info")
#        storageRedis.redis_hset("HOSTS",'foo',"MyInfo")
#        storageRedis.redis_hset("HOSTS",'bar',"MyInfo")
#        storageRedis.redis_hset("RRD_PATH",'foo',rrd_path+'/foo')
#        storageRedis.redis_hset("RRD_PATH",'bar',rrd_path+'/bar')
#        self.storage.cleanHosts(['foo','bar'])
#        result = storageRedis.redis_hkeys("HOSTS")
#        self.assertEquals(result, ['foo','bar'])
#        result = storageRedis.redis_hkeys("DELETES_HOSTS")
#        self.assertEquals(result, [])
#        # 2 data before and only one now (notify, do not delete rrd)
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        os.system("rm -Rf "+rrd_path); os.system("mkdir -p "+rrd_path)
#        storageRedis.redis_hset("INFOS@bar",'plug',"info")
#        storageRedis.redis_hset("INFOS@foo",'plug',"info")
#        storageRedis.redis_hset("HOSTS",'foo',"MyInfo")
#        storageRedis.redis_hset("HOSTS",'bar',"MyInfo")
#        storageRedis.redis_hset("RRD_PATH",'foo',rrd_path+'/foo')
#        storageRedis.redis_hset("RRD_PATH",'bar',rrd_path+'/bar')
#        os.system("mkdir -p "+rrd_path+'/foo')
#        os.system("mkdir -p "+rrd_path+'/bar')
#        self.storage.cleanHosts(['foo','gnu'])
#        result = storageRedis.redis_hkeys("HOSTS")
#        self.assertEquals(result, ['foo'])
#        self.assertTrue(os.path.isdir(rrd_path+'/bar'))
#        self.assertTrue(os.path.isdir(rrd_path+'/foo'))
#        result = storageRedis.redis_hgetall("DELETED_HOSTS")
#        self.assertEquals(result, {'bar': rrd_path+'/bar'})
#        # 2 data before remplaced by now 2 new (delete 2 last)
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("INFOS@bar",'plug',"info")
#        storageRedis.redis_hset("INFOS@foo",'plug',"info")
#        storageRedis.redis_hset("HOSTS",'foo',"MyInfo")
#        storageRedis.redis_hset("HOSTS",'bar',"MyInfo")
#        storageRedis.redis_hset("RRD_PATH",'foo',rrd_path+'/foo')
#        storageRedis.redis_hset("RRD_PATH",'bar',rrd_path+'/bar')
#        self.storage.cleanHosts(['bli','gnu'])
#        result = storageRedis.redis_hkeys("HOSTS")
#        self.assertEquals(result, [])
#        result = storageRedis.redis_hkeys("DELETED_HOSTS")
#        self.assertEquals(result, ['foo','bar'])
#        # 2 data before. 1 old deleted and one new
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("INFOS@bar",'plug',"info")
#        storageRedis.redis_hset("INFOS@foo",'plug',"info")
#        storageRedis.redis_hset("HOSTS",'foo',"MyInfo")
#        storageRedis.redis_hset("HOSTS",'bar',"MyInfo")
#        storageRedis.redis_hset("RRD_PATH",'foo',rrd_path+'/foo')
#        storageRedis.redis_hset("RRD_PATH",'bar',rrd_path+'/bar')
#        self.storage.cleanHosts(['foo','gnu'])
#        result = storageRedis.redis_hkeys("HOSTS")
#        self.assertEquals(result, ['foo'])
#        result = storageRedis.redis_hkeys("DELETED_HOSTS")
#        self.assertEquals(result, ['bar'])
#        # Must delete 2 host but first have no rrd infos (delete only the last)
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("INFOS@bar",'plug',"info")
#        storageRedis.redis_hset("INFOS@foo",'plug',"info")
#        storageRedis.redis_hset("HOSTS",'foo',"MyInfo")
#        storageRedis.redis_hset("HOSTS",'bar',"MyInfo")
#        storageRedis.redis_hset("RRD_PATH",'bar',rrd_path+'/bar')
#        self.storage.cleanHosts([])
#        result = storageRedis.redis_hkeys("HOSTS")
#        self.assertEquals(result, ['foo'])
#        result = storageRedis.redis_hkeys("DELETED_HOSTS")
#        self.assertEquals(result, ['bar'])
#        # 2 datas notify but one reappeared
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        storageRedis.redis_hset("INFOS@foo",'plug',"info")
#        storageRedis.redis_hset("HOSTS",'foo',"MyInfo")
#        storageRedis.redis_hset("DELETED_HOSTS","foo","rrdpath")
#        storageRedis.redis_hset("DELETED_HOSTS","bar","rrdpath")
#        result = storageRedis.redis_hkeys("DELETED_HOSTS")
#        self.assertEquals(result, ['foo','bar'])
#        self.storage.cleanHosts(['foo'])
#        result = storageRedis.redis_hkeys("DELETED_HOSTS")
#        self.assertEquals(result, ['bar'])
#
#
#    def sorage_write_init(self):
#        sortedTS = ['1329131100', '1329131160']
#        hostAllDatas = {
#                'Infos': {
#                    'MyInfo' : {"Plugin": "MyInfo"},
#                    'load': {'Describ': '', 'Plugin': 'load', 'Title': 'Load average', 'Vlabel': 'load', 'Base': '1000',
#                        'Infos': {
#                            'load': {'info': '5 minute load average', 'id': 'load', 'label': 'load'}
#                        },
#                        'Order': ''
#                    },
#                    'df_inode': {'Describ': '', 'Plugin': 'df_inode', 'Title': 'Inode usage in percent', 'Vlabel': '%', 'Base': '1000',
#                        'Infos': {
#                            '_dev_simfs': {'id': '_dev_simfs', 'label': '/'},
#                            '_lib_init_rw': {'id': '_lib_init_rw', 'label': '/lib/init/rw'},
#                            '_dev_shm': {'id': '_dev_shm', 'label': '/dev/shm'}
#                        },
#                        'Order': ''
#                    }
#                },
#                'Datas': {
#                    'load': {
#                        '1329131160': {'load': '2.00'},
#                        '1329131100': {'load': '1.00'}
#                    },
#                    'df_inode': {
#                        '1329131160': {'_dev_simfs': '4', '_lib_init_rw': '1', '_dev_shm': '1'},
#                        '1329131100': {'_dev_simfs': '4', '_lib_init_rw': '1', '_dev_shm': '1'}
#                    },
#                }
#            }
#        host = "127.0.0.1"
#        os.system("rm -Rf /tmp/numeter_rrds")
#        rrdPath = "/tmp/numeter_rrds/ac/123456"
#        return sortedTS, hostAllDatas, host, rrdPath
#
#    def test_storage_writeRrdtool(self):
#        # Init
#        # Empty plugin info -> True but no write
#        (sortedTS, hostAllDatas, host, rrdPath) = self.sorage_write_init()
#        del hostAllDatas['Infos']['df_inode']
#        del hostAllDatas['Infos']['load']
#        result = self.storage.writeRrdtool(sortedTS, hostAllDatas, host, rrdPath)
#        self.assertTrue(result)
#        result = os.path.exists("/tmp/numeter_rrds")
#        self.assertFalse(result)
#        # Write good datas
#        (sortedTS, hostAllDatas, host, rrdPath) = self.sorage_write_init()
#        result = self.storage.writeRrdtool(sortedTS, hostAllDatas, host, rrdPath)
#        self.assertTrue(result)
#        result = os.path.isfile(rrdPath+"/load/load.rrd")
#        self.assertTrue(result)
#        result = rrdtool.info(rrdPath+"/load/load.rrd")
#        self.assertEqual(result['last_update'], 1329131160)
#        self.assertEqual(result['ds[42].last_ds'], "2.00")
#        self.assertEqual(result['ds[42].type'], "GAUGE")
#        # Write good datas + DS type DERIVE
#        (sortedTS, hostAllDatas, host, rrdPath) = self.sorage_write_init()
#        hostAllDatas['Infos']['load']['Infos']['load']['type'] = 'DERIVE'
#        result = self.storage.writeRrdtool(sortedTS, hostAllDatas, host, rrdPath)
#        self.assertTrue(result)
#        result = rrdtool.info(rrdPath+"/load/load.rrd")
#        self.assertEqual(result['ds[42].type'], "DERIVE")
#        # Write good datas + bad DS type
#        (sortedTS, hostAllDatas, host, rrdPath) = self.sorage_write_init()
#        hostAllDatas['Infos']['load']['Infos']['load']['type'] = 'bad'
#        result = self.storage.writeRrdtool(sortedTS, hostAllDatas, host, rrdPath)
#        self.assertTrue(result)
#        result = rrdtool.info(rrdPath+"/load/load.rrd")
#        self.assertEqual(result['ds[42].type'], "GAUGE")
#        # Try with plugin and no infos
#        (sortedTS, hostAllDatas, host, rrdPath) = self.sorage_write_init()
#        del hostAllDatas['Infos']['load']['Infos']
#        result = self.storage.writeRrdtool(sortedTS, hostAllDatas, host, rrdPath)
#        self.assertTrue(result)
#        result = os.path.exists(rrdPath+"/load/")
#        self.assertFalse(result)
#        # Try with lost datas for load plugin
#        (sortedTS, hostAllDatas, host, rrdPath) = self.sorage_write_init()
#        del hostAllDatas['Datas']['load']
#        result = self.storage.writeRrdtool(sortedTS, hostAllDatas, host, rrdPath)
#        self.assertTrue(result)
#        result = os.path.isfile(rrdPath+"/load/load.rrd")
#        self.assertTrue(result)
#        # Try with lost timestamp for load plugin
#        (sortedTS, hostAllDatas, host, rrdPath) = self.sorage_write_init()
#        del hostAllDatas['Datas']['load']['1329131160']
#        result = self.storage.writeRrdtool(sortedTS, hostAllDatas, host, rrdPath)
#        self.assertTrue(result)
#        result = os.path.exists(rrdPath+"/load/")
#        self.assertTrue(result)
#        result = rrdtool.info(rrdPath+"/load/load.rrd")
#        self.assertEqual(result['last_update'], 1329131100)
#        self.assertEqual(result['ds[42].last_ds'], "1.00")
#        # Try write error
#        (sortedTS, hostAllDatas, host, rrdPath) = self.sorage_write_init()
#        os.system("touch /tmp/numeter_rrds")
#        result = self.storage.writeRrdtool(sortedTS, hostAllDatas, host, rrdPath)
#        self.assertTrue(result)
#        result = os.path.isfile(rrdPath+"/load/load.rrd")
#        self.assertFalse(result)
#        # Try unsorted datas
#        (sortedTS, hostAllDatas, host, rrdPath) = self.sorage_write_init()
#        sortedTS = ['1329131160','1329131100']
#        result = self.storage.writeRrdtool(sortedTS, hostAllDatas, host, rrdPath)
#        self.assertTrue(result)
#        result = os.path.isfile(rrdPath+"/load/load.rrd")
#        self.assertTrue(result)
#        result = rrdtool.info(rrdPath+"/load/load.rrd")
#        self.assertEqual(result['last_update'], 1329131160)
#        self.assertEqual(result['ds[42].last_ds'], "2.00")
#        # Update a fake rrd
#        (sortedTS, hostAllDatas, host, rrdPath) = self.sorage_write_init()
#        os.system("mkdir -p "+rrdPath+"/load")
#        os.system("echo 1 > "+rrdPath+"/load/load.rrd")
#        result = self.storage.writeRrdtool(sortedTS, hostAllDatas, host, rrdPath) # Update
#        self.assertTrue(result)
#        try:
#            rrdtool.info(rrdPath+"/load/load.rrd")
#            self.assertTrue(False)
#        except:
#            self.assertTrue(True)
##        self.assertRaises(Exception,rrdtool.info(rrdPath+"/load/load.rrd"))
#        #
#        (sortedTS, hostAllDatas, host, rrdPath) = self.sorage_write_init()
#        os.system("mkdir -p "+rrdPath+"/load")
#        os.system("touch "+rrdPath+"/load/load.rrd")
#        result = self.storage.writeRrdtool(sortedTS, hostAllDatas, host, rrdPath) # Update
#        self.assertTrue(result)
#        try:
#            rrdtool.info(rrdPath+"/load/load.rrd")
#            self.assertTrue(False)
#        except:
#            self.assertTrue(True)
##        self.assertRaises(Exception,rrdtool.info(rrdPath+"/load/load.rrd"))
#
#
#
#
#    def test_storage_workerRedis(self):
#        # Init
#        sema = myFakeSema()
#        collectorLine = {'host': '127.0.0.1', 'password': 'password', 'db': '1'}
#        hostList = ['hostFoo', 'hostBar']
#        # Start connexion storage (db2)
#        self.storage._redis_storage_db = 2
#        storageRedis = self.storage.redisStartConnexion()
#        self.storage._redis_connexion = storageRedis
#        self.storage._rrd_path_md5_char = 2
#        # Start connexion client (db1)
#        self.storage._redis_storage_db = 1
#        collectorRedis = self.storage.redisStartConnexion()
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        os.system("rm -Rf /tmp/numeter_rrds")
#        # Init MyInfo
#        plugDf = '{"Plugin": "df", "Infos": { "root":{"id": "root"}, "home":{"id": "home"}}}'
#        MyInfoFoo = '{ "Plugin": "MyInfo", "ID": "hostFoo", "Name": "fooName"}'
#        MyInfoBar = '{ "Plugin": "MyInfo", "ID": "hostBar", "Name": "barName"}'
#        collectorRedis.redis_hset("INFOS@hostFoo","df",plugDf)
#        collectorRedis.redis_hset("INFOS@hostBar","df",plugDf)
#        collectorRedis.redis_hset("INFOS@hostFoo","MyInfo",MyInfoFoo)
#        collectorRedis.redis_hset("INFOS@hostBar","MyInfo",MyInfoBar)
#        # Init set datas for getDatas
#        self.storage._max_data_by_hosts = 3
#        collectorRedis.redis_zadd("TS@hostFoo",'1329297400',1329297400)
#        collectorRedis.redis_zadd("TS@hostFoo",'1329297460',1329297460)
#        collectorRedis.redis_zadd("TS@hostBar",'1329297400',1329297400)
#        collectorRedis.redis_zadd("TS@hostBar",'1329297460',1329297460)
#        collectorRedis.redis_zadd("DATAS@hostFoo",'{"Plugin":"df","TimeStamp":"1329297400","Values":{"root": "15","home":"30"}}',1329297400)
#        collectorRedis.redis_zadd("DATAS@hostFoo",'{"Plugin":"df","TimeStamp":"1329297460","Values":{"root": "16","home":"32"}}',1329297460)
#        collectorRedis.redis_zadd("DATAS@hostBar",'{"Plugin":"df","TimeStamp":"1329297400","Values":{"root": "10","home":"12"}}',1329297400)
#        collectorRedis.redis_zadd("DATAS@hostBar",'{"Plugin":"df","TimeStamp":"1329297460","Values":{"root": "11","home":"15"}}',1329297460)
#
#        result = self.storage.workerRedis(1,sema,collectorLine,hostList)
#        self.assertEqual(result, True)
#
#        # Test redis storage Infos
#        # Check HOSTS
#        S_INFO_myinfo =     {'hostFoo': '{"Name": "fooName", "HostIDHash": "d2", "ID": "hostFoo", "HostIDFiltredName": "hostFoo", "Plugin": "MyInfo"}',
#                             'hostBar': '{"Name": "barName", "HostIDHash": "48", "ID": "hostBar", "HostIDFiltredName": "hostBar", "Plugin": "MyInfo"}'}
#        result = storageRedis.redis_hgetall("HOSTS")
#        self.assertEquals(result, S_INFO_myinfo)
#        # Check HOST_ID
#        S_HOST_ID =  {'hostFoo': 'd2', 'hostBar': '48'}
#        result = storageRedis.redis_hgetall("HOST_ID")
#        self.assertEquals(result, S_HOST_ID)
#        # Check RRD_PATH
#        S_RRD_PATH = {'hostFoo': '/tmp/numeter_rrds/d2/hostFoo', 'hostBar': '/tmp/numeter_rrds/48/hostBar'}
#        result = storageRedis.redis_hgetall("RRD_PATH")
#        self.assertEquals(result, S_RRD_PATH)
#        # Check INFOS@host
#        result = storageRedis.redis_hkeys("INFOS@hostFoo")
#        self.assertEquals(result,['df'])
#        result = storageRedis.redis_hget("INFOS@hostFoo","df")
#        self.assertEquals(result, plugDf)
#        result = storageRedis.redis_hget("HOSTS","hostFoo")
#        self.assertEquals(result, S_INFO_myinfo['hostFoo'])
#        result = storageRedis.redis_hkeys("INFOS@hostBar")
#        self.assertEquals(result,['df'])
#        result = storageRedis.redis_hget("INFOS@hostBar","df")
#        self.assertEquals(result, plugDf)
#        result = storageRedis.redis_hget("HOSTS","hostBar")
#        self.assertEquals(result, S_INFO_myinfo['hostBar'])
#        # Test rrd write
#        result = os.path.isfile("/tmp/numeter_rrds/d2/hostFoo/df/root.rrd")
#        self.assertTrue(result)
#        result = os.path.isfile("/tmp/numeter_rrds/d2/hostFoo/df/home.rrd")
#        self.assertTrue(result)
#        result = rrdtool.info("/tmp/numeter_rrds/d2/hostFoo/df/root.rrd")
#        self.assertEqual(result['last_update'], 1329297460)
#        self.assertEqual(result['ds[42].last_ds'], "16")
#        self.assertEqual(result['ds[42].type'], "GAUGE")
#        result = rrdtool.info("/tmp/numeter_rrds/d2/hostFoo/df/home.rrd")
#        self.assertEqual(result['last_update'], 1329297460)
#        self.assertEqual(result['ds[42].last_ds'], "32")
#        self.assertEqual(result['ds[42].type'], "GAUGE")
#        result = os.path.isfile("/tmp/numeter_rrds/48/hostBar/df/root.rrd")
#        self.assertTrue(result)
#        result = os.path.isfile("/tmp/numeter_rrds/48/hostBar/df/home.rrd")
#        self.assertTrue(result)
#        result = rrdtool.info("/tmp/numeter_rrds/48/hostBar/df/root.rrd")
#        self.assertEqual(result['last_update'], 1329297460)
#        self.assertEqual(result['ds[42].last_ds'], "11")
#        self.assertEqual(result['ds[42].type'], "GAUGE")
#        result = rrdtool.info("/tmp/numeter_rrds/48/hostBar/df/home.rrd")
#        self.assertEqual(result['last_update'], 1329297460)
#        self.assertEqual(result['ds[42].last_ds'], "15")
#        self.assertEqual(result['ds[42].type'], "GAUGE")
#        # Test clear db collecteur
#        result = collectorRedis.redis_zrangebyscore("TS@hostFoo",'+inf','+inf')
#        self.assertEqual(result, [])
#        result = collectorRedis.redis_zrangebyscore("TS@hostBar",'+inf','+inf')
#        self.assertEqual(result, [])
#        result = collectorRedis.redis_zrangebyscore("DATAS@hostFoo",'+inf','+inf')
#        self.assertEqual(result, [])
#        result = collectorRedis.redis_zrangebyscore("DATAS@hostBar",'+inf','+inf')
#        self.assertEqual(result, [])
#
#
#
#    def test_storage_cleanOldRRD(self):
#        # Start connexion storage (db2)
#        self.storage._redis_storage_db = 2
#        storageRedis = self.storage.redisStartConnexion()
#        self.storage._redis_connexion = storageRedis
#        self.storage._rrd_clean_time = 1 # 1h
#        rrdPath = '/tmp/rrd_unittest/myhost'
#        self.storage._rrd_path = rrdPath
#        self.storage._rrd_delete = False
#
#        # Test with no TimeStamp
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        result = storageRedis.redis_get("LAST_RRD_CLEAN")
#        self.assertEqual(result, None)
#        self.storage.cleanOldRRD()
#        result = storageRedis.redis_get("LAST_RRD_CLEAN")
#        self.assertTrue(re.match('^[0-9]{10}$', result))
#        resultLast = result
#        # start too soon : do nothing return empty
#        result = self.storage.cleanOldRRD()
#        self.assertEquals(result, [])
#        result = storageRedis.redis_get("LAST_RRD_CLEAN")
#        self.assertEquals(resultLast,result)
#        #
#        # RRD DELETE FALSE
#        # Set old ts. do run but no file to delete
#        self.storage._rrd_delete = False
#        os.system("rm -rf "+rrdPath)
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        result = storageRedis.redis_set("LAST_RRD_CLEAN",'0000000000')
#        os.system("mkdir -p "+rrdPath+'/foo/') ; os.system("touch "+rrdPath+'/foo/ds.rrd')
#        result = self.storage.cleanOldRRD()
#        self.assertEquals(result, [])
#        result = storageRedis.redis_get("OLD_RRD")
#        self.assertEquals(result, '[]')
#        # same with data to delete
#        self.storage._rrd_clean_time = 0 # 0h
#        os.system("rm -rf "+rrdPath)
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        result = storageRedis.redis_set("LAST_RRD_CLEAN",'0000000000')
#        os.system("mkdir -p "+rrdPath+'/foo/') ; os.system("touch "+rrdPath+'/foo/ds.rrd')
#        result = self.storage.cleanOldRRD()
#        self.assertEquals(result, ['/tmp/rrd_unittest/myhost/foo/ds.rrd'])
#        result = storageRedis.redis_get("OLD_RRD")
#        self.assertEquals(result, '["/tmp/rrd_unittest/myhost/foo/ds.rrd"]')
#        #
#        # RRD DELETE TRUE
#        # Set old ts. do run but no file to delete unless an empty dir
#        self.storage._rrd_delete = True
#        self.storage._rrd_clean_time = 1 # 0h
#        os.system("rm -rf "+rrdPath)
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        result = storageRedis.redis_set("LAST_RRD_CLEAN",'0000000000')
#        os.system("mkdir -p "+rrdPath+'/foo/') ; os.system("touch "+rrdPath+'/foo/ds.rrd')
#        os.system("mkdir -p "+rrdPath+'/bar/')
#        result = self.storage.cleanOldRRD()
#        self.assertEquals(result, [])
#        result = os.path.isfile(rrdPath+'/foo/ds.rrd')
#        self.assertTrue(result)
#        result = os.path.isdir(rrdPath+'/bar')
#        self.assertFalse(result)
#        # same with data to delete and empty dir
#        self.storage._rrd_delete = True
#        self.storage._rrd_clean_time = 0 # 0h
#        os.system("rm -rf "+rrdPath)
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        result = storageRedis.redis_set("LAST_RRD_CLEAN",'0000000000')
#        os.system("mkdir -p "+rrdPath+'/foo/') ; os.system("touch "+rrdPath+'/foo/ds.rrd')
#        os.system("mkdir -p "+rrdPath+'/bar/')
#        result = self.storage.cleanOldRRD()
#        self.assertEquals(result, ['/tmp/rrd_unittest/myhost/foo/ds.rrd'])
#        result = os.path.isfile(rrdPath+'/foo/ds.rrd')
#        self.assertFalse(result)
#        result = os.path.isdir(rrdPath+'/foo')
#        self.assertFalse(result)
#        result = os.path.isdir(rrdPath+'/bar')
#        self.assertFalse(result)
#
#
## Fake sema
#class myFakeSema(object):
#    def __init__(self):
#        return
#    def release(self):
#        return

#!/usr/bin/env python
# -*- coding: utf-8 -*-
