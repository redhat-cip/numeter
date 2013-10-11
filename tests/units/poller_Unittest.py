#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import mock
from mock import call

myPath = os.path.abspath(os.path.dirname(__file__))

import numeter.poller
from test_utils import FakeRedis
from numeter.redis import RedisConnect

import base as test_base

class PollerTestCase(test_base.TestCase):

    def setUp(self):
        super(PollerTestCase, self).setUp()
        self.getgloballog_orig = numeter.poller.Poller.getgloballog
        numeter.poller.Poller.getgloballog = mock.MagicMock()
        self.poller = numeter.poller.Poller(myPath+"/poller_unittest.cfg")
        self.poller._logger = myFakeLogger()

    def tearDown(self):
        super(PollerTestCase, self).tearDown()
        numeter.poller.Poller.getgloballog = numeter.poller.Poller.getgloballog

    def test_poller_pollerTimeToGo(self):
        self.poller._poller_time            = 60
        self.poller._plugins_refresh_time   = 300
        # First start no file (need refresh and start)
        with mock.patch('time.time', mock.MagicMock()) as time_mock, \
             mock.patch('os.path.isfile', mock.MagicMock()) as isfile_mock, \
             mock.patch('__builtin__.open', mock.mock_open(), create=True) as file_mock:
                handle = file_mock()
                isfile_mock.return_value = False
                time_mock.return_value = 1000000000
                result = self.poller.pollerTimeToGo()
                file_mock.assert_called_with(self.poller._poller_time_file, 'w')
                handle.write.assert_called_once_with('%s %s'
                        % (time_mock.return_value, time_mock.return_value))
                self.assertTrue(result)
                self.assertTrue(self.poller._need_refresh)
        # Try to run quick poll (too soon)
        with mock.patch('time.time', mock.MagicMock()) as time_mock, \
             mock.patch('os.path.isfile', mock.MagicMock()) as isfile_mock, \
             mock.patch('__builtin__.open', mock.mock_open(), create=True) as file_mock:
                time_mock.return_value = 1000000002
                file_mock.return_value.read.return_value = '1000000001 1000000001'
                isfile_mock.return_value = True
                result = self.poller.pollerTimeToGo()
                self.assertFalse(result)
                self.assertFalse(self.poller._need_refresh)
        # one poller_time after, update only datas
        with mock.patch('time.time', mock.MagicMock()) as time_mock, \
             mock.patch('os.path.isfile', mock.MagicMock()) as isfile_mock, \
             mock.patch('__builtin__.open', mock.mock_open(), create=True) as file_mock:
                handle = file_mock()
                time_mock.return_value = 1000000001 + self.poller._poller_time
                file_mock.return_value.read.return_value = '1000000001 1000000001'
                isfile_mock.return_value = True
                result = self.poller.pollerTimeToGo()
                self.assertTrue(result)
                self.assertFalse(self.poller._need_refresh)
                handle.write.assert_called_once_with('%s %s'
                        % ( time_mock.return_value, '1000000001'))
        # one refresh time after update infos
        with mock.patch('time.time', mock.MagicMock()) as time_mock, \
             mock.patch('os.path.isfile', mock.MagicMock()) as isfile_mock, \
             mock.patch('__builtin__.open', mock.mock_open(), create=True) as file_mock:
                handle = file_mock()
                time_mock.return_value = 1000000001 + self.poller._plugins_refresh_time
                file_mock.return_value.read.return_value = '1000000001 1000000001'
                isfile_mock.return_value = True
                result = self.poller.pollerTimeToGo()
                self.assertTrue(result)
                self.assertTrue(self.poller._need_refresh)
                handle.write.assert_called_once_with('%s %s'
                        % ( time_mock.return_value, time_mock.return_value))
        # Make corrupted time file
        with mock.patch('time.time', mock.MagicMock()) as time_mock, \
             mock.patch('os.path.isfile', mock.MagicMock()) as isfile_mock, \
             mock.patch('__builtin__.open', mock.mock_open(), create=True) as file_mock:
                handle = file_mock()
                time_mock.return_value = 1000000001 + self.poller._plugins_refresh_time
                file_mock.return_value.read.return_value = ''
                isfile_mock.return_value = True
                result = self.poller.pollerTimeToGo()
                self.assertTrue(result)
                self.assertTrue(self.poller._need_refresh)
                handle.write.assert_called_once_with('%s %s'
                        % ( time_mock.return_value, time_mock.return_value))

    def test_poller_getMyInfo(self):
        # Test defaults values
        result = self.poller.getMyInfo()
        self.assertEquals(result[0]['Plugin'], "MyInfo")
        self.assertEquals(result[0]['Name'], socket.gethostname())
        # Test with setted values
        self.poller._myInfo_name        = "foo"
        self.poller._myInfo_hostID      = "1234567"
        self.poller._myInfo_description = "foobar"
        result = self.poller.getMyInfo()
        self.assertEquals(result[0]['ID'], "1234567")
        self.assertEquals(result[0]['Description'], "foobar")
        self.assertEquals(result[0]['Name'], 'foo')

    # TODO test cache : self._cache.get_value(key)
    def test_poller_sendInfo(self):
        # Mock _sendMsg
        orig_sendMsg = self.poller._sendMsg
        self.poller._sendMsg = mock.MagicMock(return_value=True)
        # Test good values 2 plugins
        result = self.poller._sendInfo([{'Plugin':"foo", 'Infos':{} },{'Plugin':"bar"}])
        self.assertEquals(result,['foo', 'bar'])
        calls = [
                 call(msgContent='{"Infos": {}, "Plugin": "foo"}',
                      msgType='info', plugin='foo'),
                 call(msgContent='{"Plugin": "bar"}',
                      msgType='info', plugin='bar')
                ]
        self.poller._sendMsg.assert_has_calls(calls)
        # Test with empty value
        result = self.poller._sendInfo([])
        self.assertEquals(result,[])
        # Good value without plugin name
        result = self.poller._sendInfo([{'Title':"foo", }])
        self.assertEquals(result, [])
        # Restore _sendMsg
        self.poller._sendMsg = orig_sendMsg

    # TODO add test for DERIVE, COUNTER values (lastValue = self._cache.get_value(key))
    def test_poller_sendData(self):

        class fake_message(object):
            def __init__(self, poller):
                self.poller = poller
            def __enter__(self):
                # Mock _store_and_forward_sendMsg
                self.orig_store_and_forward_sendMsg = self.poller._store_and_forward_sendMsg
                self.poller._store_and_forward_sendMsg = mock.MagicMock(return_value=True)
                # Mock _cache
                self.orig_cache = self.poller._cache
                self.poller._cache = mock.MagicMock()
                self.poller._cache.get_value = mock.MagicMock(return_value=None)
                # Mock _store_and_forward
                self.poller._store_and_forward = mock.MagicMock()
                self.poller._store_and_forward.consume = mock.MagicMock(return_value=[])
                return self
            def __exit__(self, *args):
                # Restore _store_and_forward_sendMsg
                self.poller._store_and_forward_sendMsg = self.orig_store_and_forward_sendMsg
                # Restore _cache.get_value
                self.poller._cache = self.orig_cache

        with fake_message(self.poller) as faker:
            # send good value
            faker.poller._sendData([{"TimeStamp": "1328624580", "Values": {"entropy": "146"}, "Plugin": "entropy"},
                                    {"TimeStamp": "1328624760", "Values": {"load": "0.00"}, "Plugin": "load"}])
            calls = [call(msgContent='{"TimeStamp": "1328624580", "Values": {"entropy": "146"}, "Plugin": "entropy"}', msgType='data', plugin='entropy'),
                     call(msgContent='{"TimeStamp": "1328624760", "Values": {"load": "0.00"}, "Plugin": "load"}', msgType='data', plugin='load')]
            faker.poller._store_and_forward_sendMsg.assert_has_calls(calls)
        # set Empty value
        with fake_message(self.poller) as faker:
            faker.poller._sendData([])
            calls = []
            faker.poller._store_and_forward_sendMsg.assert_has_calls(calls)
        # send value without Plugin name
        with fake_message(self.poller) as faker:
            faker.poller._sendData([{"TimeStamp": "1328624580", "Values": {"entropy": "146"}}])
            calls = []
            faker.poller._store_and_forward_sendMsg.assert_has_calls(calls)

# Fake log
class myFakeLogger(object):
    def __init__(self):
        return
    def critical(self,string):
        return
    def error(self,string):
        return
    def warning(self,string):
        return
    def info(self,string):
        return
    def debug(self,string):
        return
