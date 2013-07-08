#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket
import mock

myPath = os.path.abspath(os.path.dirname(__file__))

sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../../common'))
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../../poller/module'))

import myRedisConnect
from numeter_poller import *
from test_utils import FakeRedis

import base as test_base


class PollerTestCase(test_base.TestCase):

    def setUp(self):
        super(PollerTestCase, self).setUp()
        self.poller = myPoller(myPath+"/poller_unittest.cfg")

    def tearDown(self):
        super(PollerTestCase, self).tearDown()

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

    def test_poller_writeInfo(self):
        self.poller._redis_connexion = FakeRedis()
        # Test good values 2 plugins
        result = self.poller.writeInfo([{'Plugin':"foo", },{'Plugin':"bar"}])
        self.assertEquals(result,['foo', 'bar'])
        expected_result = {'INFOS': {
                            'foo': '{"Plugin": "foo"}',
                            'bar': '{"Plugin": "bar"}'}
                          }
        self.assertEquals(expected_result, self.poller._redis_connexion.get_and_flush_hset())
        # Test with empty value
        result = self.poller.writeInfo([])
        self.assertEquals(result,[])
        # Good value without plugin name
        result = self.poller.writeInfo([{'Title':"foo", }])
        self.assertEquals(result, [])

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


    def test_poller_writeData(self):
        self.poller._redis_connexion = FakeRedis()
        # send good value
        self.poller.writeData([{"TimeStamp": "1328624580", "Values": {"entropy": "146"}, "Plugin": "entropy"},
                                {"TimeStamp": "1328624760", "Values": {"load": "0.00"}, "Plugin": "load"}])
        expected_result = {
            'TimeStamp': { 1328624760: ['1328624760'], 1328624580: ['1328624580']}, 
            'DATAS': {
                 1328624760: ['{"TimeStamp": "1328624760", "Values": {"load": "0.00"}, "Plugin": "load"}'], 
                 1328624580: ['{"TimeStamp": "1328624580", "Values": {"entropy": "146"}, "Plugin": "entropy"}']
            }
        } 
        self.assertEquals(expected_result,
                          self.poller._redis_connexion.get_and_flush_zadd())
        # set Empty value
        self.poller.writeData([])
        expected_result = {} 
        self.assertEquals(expected_result,
                          self.poller._redis_connexion.get_and_flush_zadd())
        # send value without Plugin name
        self.poller.writeData([{"TimeStamp": "1328624580", "Values": {"entropy": "146"}}])
        expected_result = {} 
        self.assertEquals(expected_result,
                          self.poller._redis_connexion.get_and_flush_zadd())

    def test_poller_redisStartConnexion(self):
        called = []
        def myRedisConnect__init__(self, *args, **kwargs):
            called.append("TESTED")
            self._error=False
        self.stubs.Set(myRedisConnect, '__init__', myRedisConnect__init__)
        self.poller.redisStartConnexion()
        self.assertEqual(len(called), 1)
