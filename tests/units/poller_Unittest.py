#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import socket

myPath = os.path.abspath(os.path.dirname(__file__))

sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../../common'))
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../../poller/module'))

import myRedisConnect
from numeter_poller import *
from test_utils import FakeRedis

import base as test_base


class PollerTestCase(test_base.TestCase):

#    def get_init_munin(self):
#        # Start munin
#        os.system("/etc/init.d/munin-node start >/dev/null")
#        os.system("echo -e 'fetch df\nquit' | nc 127.0.0.1 4949 >/dev/null && true")


    def setUp(self):
        super(PollerTestCase, self).setUp()
#        os.system("rm -f /tmp/poller_last.unittest")
#        os.system("kill -9 $(cat /var/run/redis/redis-unittest.pid 2>/dev/null) 2>/dev/null")
#        os.system('kill -9 $(pgrep -f "redis-server '+myPath+'/redis_unittest.conf")')
#        os.system("redis-server "+myPath+"/redis_unittest.conf")
#        os.system("while ! netstat -laputn | grep 8888 > /dev/null; do true; done ")
#        os.system("redis-cli -a password -p 8888 ping >/dev/null")
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        self.poller = myPoller(myPath+"/poller_unittest.cfg")
#        self.get_init_munin()
#
#
    def tearDown(self):
        super(PollerTestCase, self).tearDown()
#        os.system("kill -9 $(cat /var/run/redis/redis-unittest.pid)")
#        os.system('kill -9 $(pgrep -f "redis-server '+myPath+'/redis_unittest.conf")')
#        os.system("rm -f /tmp/poller_last.unittest")
#
#
#    def test_poller_rediscleanDataExpired(self):
#        # Get now TS
#        now              = time.strftime("%Y %m %d %H:%M", time.localtime())
#        nowTimestamp     = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M')) # "%.0f" % supprime le .0 aprés le
#        # Start connexion
#        self.poller._redis_connexion = self.poller.redisStartConnexion()
#        # Send one new and one old TS
#        self.poller._redis_connexion.redis_zadd("TimeStamp","0000000000",0000000000)
#        self.poller._redis_connexion.redis_zadd("TimeStamp",nowTimestamp,nowTimestamp)
#        # Check
#        result = self.poller._redis_connexion.redis_zrangebyscore("TimeStamp",'-inf','+inf')
#        self.assertEqual(result, ['0000000000', nowTimestamp])
#        # Send one new and one old Data
#        self.poller._redis_connexion.redis_zadd("DATAS","oldData",0000000000)
#        self.poller._redis_connexion.redis_zadd("DATAS","newData",nowTimestamp)
#        # Check
#        result = self.poller._redis_connexion.redis_zrangebyscore("DATAS",'-inf','+inf')
#        self.assertEqual(result, ['oldData', 'newData'])
#        # Clear old data only
#        self.poller.rediscleanDataExpired()
#        # Check TimeStamp and DATAS
#        result = self.poller._redis_connexion.redis_zrangebyscore("TimeStamp",'-inf','+inf')
#        self.assertEqual(result, [nowTimestamp])
#        result = self.poller._redis_connexion.redis_zrangebyscore("DATAS",'-inf','+inf')
#        self.assertEqual(result, ['newData'])
#
#
#    def test_poller_pollerTimeToGo(self):
#        now              = time.strftime("%Y %m %d %H:%M", time.localtime())
#        nowTimestamp     = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M')) # "%.0f" % supprime le .0 aprés le
#        # Init
#        self.poller._poller_time            = 60
#        self.poller._plugins_refresh_time   = 300
#        # At start refresh plugin not needed
#        self.assertFalse(self.poller._need_refresh)
#        # First start no file (need refresh and true)
#        os.system("rm -f /tmp/poller_last.unittest")
#        result = self.poller.pollerTimeToGo()
#        self.assertTrue(result)
#        self.assertTrue(self.poller._need_refresh)
#        # Make corrupt /tmp/poller_last.unittest
#        os.system(":>/tmp/poller_last.unittest")
#        result = self.poller.pollerTimeToGo()
#        self.assertTrue(result)
#        # Refresh needed
#        self.assertTrue(self.poller._need_refresh)
#        # Try to run quick poll (too soon)
#        result = self.poller.pollerTimeToGo()
#        self.assertFalse(result)
#        self.assertFalse(self.poller._need_refresh)
#        # change time in file for poller only, no refresh
#        os.system("echo '"+str(int(nowTimestamp)-60)+" "+nowTimestamp+"' >/tmp/poller_last.unittest")
#        result = self.poller.pollerTimeToGo()
#        self.assertTrue(result)
#        self.assertFalse(self.poller._need_refresh)
#        # change time in file for poller and refresh
#        os.system("echo '"+str(int(nowTimestamp)-60)+" "+str(int(nowTimestamp)-300)+"' >/tmp/poller_last.unittest")
#        result = self.poller.pollerTimeToGo()
#        self.assertTrue(result)
#        self.assertTrue(self.poller._need_refresh)
#
#    def test_poller_getMyInfo(self):
#        # Test defaults values
#        result = self.poller.getMyInfo()
##        self.assertEquals(result[0]['Step'], "60")
#        self.assertEquals(result[0]['Plugin'], "MyInfo")
#        self.assertEquals(result[0]['Name'], socket.gethostname())
#        # Test set some values
#        self.poller._myInfo_name        = "foo"
#        self.poller._myInfo_hostID      = "123456"
#        self.poller._myInfo_description = "foobar"
#        result = self.poller.getMyInfo()
#        self.assertEquals(result[0]['ID'], "123456")
#        self.assertEquals(result[0]['Description'], "foobar")
#        self.assertEquals(result[0]['Name'], 'foo')
#
#    def test_poller_writeInfo(self):
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        self.poller._redis_connexion = self.poller.redisStartConnexion()
#        # Test good values 2 plugins
#        result = self.poller.writeInfo([{'Plugin':"foo", },{'Plugin':"bar"}])
#        self.assertEquals(result,['foo', 'bar'])
#        result = self.poller._redis_connexion.redis_hkeys("INFOS")
#        self.assertEquals(result, ['foo', 'bar'])
#        result = self.poller._redis_connexion.redis_hget("INFOS","foo")
#        self.assertEquals(result, '{"Plugin": "foo"}') # (json string)
#        # Test with empty value
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        result = self.poller.writeInfo([])
#        self.assertEquals(result,[])
#        result = self.poller._redis_connexion.redis_hkeys("INFOS")
#        self.assertEquals(result, [])
#        # Good value without plugin name
#        self.poller.writeInfo([{'Title':"foo", }])
#        result = self.poller._redis_connexion.redis_hkeys("INFOS")
#        self.assertEquals(result, [])
#
#    def test_poller_cleanInfo(self):
#        self.poller._redis_connexion = self.poller.redisStartConnexion()
#        pollerRedis = self.poller._redis_connexion
#        # No data before (dont delete no data after)
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        self.poller.cleanInfo([{'Plugin':"foo", },{'Plugin':"bar"}])
#        result = pollerRedis.redis_hkeys("INFOS")
#        self.assertEquals(result, [])
#        # 2 data before and same data now
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        pollerRedis.redis_hset("INFOS",'foo','foo')
#        pollerRedis.redis_hset("INFOS",'bar','bar')
#        self.poller.cleanInfo(["foo","bar"])
#        result = pollerRedis.redis_hkeys("INFOS")
#        self.assertEquals(result, ['foo', 'bar'])
#        # 2 data before and only one now
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        pollerRedis.redis_hset("INFOS",'foo','foo')
#        pollerRedis.redis_hset("INFOS",'bar','bar')
#        self.poller.cleanInfo(["foo"])
#        result = pollerRedis.redis_hkeys("INFOS")
#        self.assertEquals(result, ['foo'])
#        # 2 data before and 2 new
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        pollerRedis.redis_hset("INFOS",'foo','foo')
#        pollerRedis.redis_hset("INFOS",'bar','bar')
#        self.poller.cleanInfo(["gnu","bli"])
#        result = pollerRedis.redis_hkeys("INFOS")
#        self.assertEquals(result, [])
#        # 2 data before and old + 2 new now
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        pollerRedis.redis_hset("INFOS",'foo','foo')
#        pollerRedis.redis_hset("INFOS",'bar','bar')
#        self.poller.cleanInfo(["foo","bar","gnu","bli"])
#        result = pollerRedis.redis_hkeys("INFOS")
#        self.assertEquals(result, ['foo', 'bar'])
#        # 2 data before and 1 old delete and one new now
#        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
#        pollerRedis.redis_hset("INFOS",'foo','foo')
#        pollerRedis.redis_hset("INFOS",'bar','bar')
#        self.poller.cleanInfo(["foo","gnu"])
#        result = pollerRedis.redis_hkeys("INFOS")
#        self.assertEquals(result, ['foo'])


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
