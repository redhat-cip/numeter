#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import mock
from mock import call

myPath = os.path.abspath(os.path.dirname(__file__))

sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../../common'))
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../../poller/module'))

import numeter_poller
from test_utils import FakeRedis
from myRedisConnect import myRedisConnect

import base as test_base


class PollerTestCase(test_base.TestCase):

    def setUp(self):
        super(PollerTestCase, self).setUp()
        self.getgloballog_orig = numeter_poller.myPoller.getgloballog
        numeter_poller.myPoller.getgloballog = mock.MagicMock()
        self.poller = numeter_poller.myPoller(myPath+"/poller_unittest.cfg")
        self.poller._logger = myFakeLogger()

    def tearDown(self):
        super(PollerTestCase, self).tearDown()
        numeter_poller.myPoller.getgloballog = numeter_poller.myPoller.getgloballog

    def test_poller_rediscleanDataExpired(self):
        now              = time.strftime("%Y %m %d %H:%M", time.localtime())
        nowTimestamp     = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M'))
        # Start connexion
        self.poller._redis_connexion = FakeRedis()
        self.poller._redis_data_expire_time = 1 # 1 min
        # Set a old with TS, one old data without TS and a recent
        # data (must delete all old things)
        self.poller._redis_connexion.redis_zadd("TimeStamp", "1111111111",
                                                1111111111)
        self.poller._redis_connexion.redis_zadd("TimeStamp", nowTimestamp,
                                                nowTimestamp)
        self.poller._redis_connexion.redis_zadd("DATAS", "oldData", 1111111111)
        self.poller._redis_connexion.redis_zadd("DATAS", "oldData", 1111111112)
        self.poller._redis_connexion.redis_zadd("DATAS", "newData", nowTimestamp)
        self.poller.rediscleanDataExpired()
        result = self.poller._redis_connexion.get_and_flush_zadd()
        self.assertEquals(len(result['DATAS']),1)
        self.assertEquals(len(result['TimeStamp']),1)

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

    def test_poller_cleanInfo(self):
        self.poller._redis_connexion = FakeRedis()
        # No data before (dont delete no data after)
        self.poller._redis_connexion.hset_data = {'INFOS':{}}
        self.poller.cleanInfo([{'Plugin':"foo", },{'Plugin':"bar"}])
        self.assertEquals({'INFOS':{}},
                          self.poller._redis_connexion.get_and_flush_hset())
        # 2 data before and same data now
        self.poller._redis_connexion.redis_hset("INFOS",'foo','foo')
        self.poller._redis_connexion.redis_hset("INFOS",'bar','bar')
        self.poller.cleanInfo(["foo","bar"])
        result = self.poller._redis_connexion.redis_hkeys("INFOS")
        self.assertEquals(result, ['foo', 'bar'])
        # 2 data before and only one now
        self.poller._redis_connexion.redis_hset("INFOS",'foo','foo')
        self.poller._redis_connexion.redis_hset("INFOS",'bar','bar')
        self.poller.cleanInfo(["foo"])
        result = self.poller._redis_connexion.redis_hkeys("INFOS")
        self.assertEquals(result, ['foo'])
        # 2 data before -> delete one and add 2 new
        self.poller._redis_connexion.redis_hset("INFOS",'foo','foo')
        self.poller._redis_connexion.redis_hset("INFOS",'bar','bar')
        self.poller.cleanInfo(['foo', 'gnu', 'bli'])
        result = self.poller._redis_connexion.redis_hkeys("INFOS")
        self.assertEquals(result, ['foo'])

    # TODO test cache : self._cache.get_value(key)
    def test_poller_writeInfo(self):
        self.poller._redis_connexion = FakeRedis()
        # Mock _sendMsg
        orig_sendMsg = self.poller._sendMsg
        self.poller._sendMsg = mock.MagicMock(return_value=True)
        # Test good values 2 plugins
        result = self.poller.writeInfo([{'Plugin':"foo", 'Infos':{} },{'Plugin':"bar"}])
        self.assertEquals(result,['foo', 'bar'])
        expected_result = {'INFOS': {
                            'foo': '{"Infos": {}, "Plugin": "foo"}',
                            'bar': '{"Plugin": "bar"}'}
                          }
        self.assertEquals(expected_result, self.poller._redis_connexion.get_and_flush_hset())
        calls = [
                 call(msgContent='{"Infos": {}, "Plugin": "foo"}',
                      msgType='info', plugin='foo'),
                 call(msgContent='{"Plugin": "bar"}',
                      msgType='info', plugin='bar')
                ]
        self.poller._sendMsg.assert_has_calls(calls)
        # Test with empty value
        result = self.poller.writeInfo([])
        self.assertEquals(result,[])
        # Good value without plugin name
        result = self.poller.writeInfo([{'Title':"foo", }])
        self.assertEquals(result, [])
        # Restore _sendMsg
        self.poller._sendMsg = orig_sendMsg

    # TODO add test for DERIVE, COUNTER values (lastValue = self._cache.get_value(key))
    def test_poller_writeData(self):

        class fake_message:
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
            faker.poller._redis_connexion = FakeRedis()
            # send good value
            faker.poller.writeData([{"TimeStamp": "1328624580", "Values": {"entropy": "146"}, "Plugin": "entropy"},
                                    {"TimeStamp": "1328624760", "Values": {"load": "0.00"}, "Plugin": "load"}])
            expected_result = {
                'TimeStamp': { 1328624760: ['1328624760'], 1328624580: ['1328624580']}, 
                'DATAS': {
                     1328624760: ['{"TimeStamp": "1328624760", "Values": {"load": "0.00"}, "Plugin": "load"}'], 
                     1328624580: ['{"TimeStamp": "1328624580", "Values": {"entropy": "146"}, "Plugin": "entropy"}']
                }
            } 
            self.assertEquals(expected_result,
                              faker.poller._redis_connexion.get_and_flush_zadd())

            calls = [call(msgContent='{"TimeStamp": "1328624580", "Values": {"entropy": "146"}, "Plugin": "entropy"}', msgType='data', plugin='entropy'),
                     call(msgContent='{"TimeStamp": "1328624760", "Values": {"load": "0.00"}, "Plugin": "load"}', msgType='data', plugin='load')]
            faker.poller._store_and_forward_sendMsg.assert_has_calls(calls)
        # set Empty value
        with fake_message(self.poller) as faker:
            faker.poller.writeData([])
            expected_result = {} 
            self.assertEquals(expected_result,
                              faker.poller._redis_connexion.get_and_flush_zadd())
            calls = []
            faker.poller._store_and_forward_sendMsg.assert_has_calls(calls)
        # send value without Plugin name
        with fake_message(self.poller) as faker:
            faker.poller.writeData([{"TimeStamp": "1328624580", "Values": {"entropy": "146"}}])
            expected_result = {} 
            self.assertEquals(expected_result,
                              faker.poller._redis_connexion.get_and_flush_zadd())
            calls = []
            faker.poller._store_and_forward_sendMsg.assert_has_calls(calls)

    def test_poller_redisStartConnexion(self):
        called = []
        def myRedisConnect__init__(self, *args, **kwargs):
            called.append("TESTED")
            self._error=False
        self.stubs.Set(myRedisConnect, '__init__', myRedisConnect__init__)
        self.poller.redisStartConnexion()
        self.assertEqual(len(called), 1)

# Fake log
class myFakeLogger():
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
