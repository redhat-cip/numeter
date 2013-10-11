#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import time
import socket

myPath = os.path.abspath(os.path.dirname(__file__))

from numeter.poller import Poller

class PollerTestCase(unittest.TestCase):

    def setUp(self):
        os.system("rm -f /tmp/poller_last.unittest")
        os.system("kill -9 $(cat /tmp/redis-unittest.pid 2>/dev/null) 2>/dev/null")
        os.system('kill -9 $(pgrep -f "redis-server '+myPath+'/redis_unittest.conf")')
        os.system("redis-server "+myPath+"/redis_unittest.conf")
        os.system("while ! netstat -laputn | grep 8888 > /dev/null; do true; done ")
        os.system("redis-cli -a password -p 8888 ping >/dev/null")
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        self.poller = Poller(myPath+"/poller_unittest.cfg")

    def tearDown(self):
        os.system("kill -9 $(cat /tmp/redis-unittest.pid)")
        os.system('kill -9 $(pgrep -f "redis-server '+myPath+'/redis_unittest.conf")')
        os.system("rm -f /tmp/poller_last.unittest")

    def test_poller_rediscleanDataExpired(self):
        # Get now TS
        now              = time.strftime("%Y %m %d %H:%M", time.localtime())
        nowTimestamp     = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M')) # "%.0f" % supprime le .0 aprés le
        # Start connexion
        self.poller._redis_connexion = self.poller.redisStartConnexion()
        # Send one new and one old TS
        self.poller._redis_connexion.redis_zadd("TimeStamp","0000000000",0000000000)
        self.poller._redis_connexion.redis_zadd("TimeStamp",nowTimestamp,nowTimestamp)
        # Check
        result = self.poller._redis_connexion.redis_zrangebyscore("TimeStamp",'-inf','+inf')
        self.assertEqual(result, ['0000000000', nowTimestamp])
        # Send one new and one old Data
        self.poller._redis_connexion.redis_zadd("DATAS","oldData",0000000000)
        self.poller._redis_connexion.redis_zadd("DATAS","newData",nowTimestamp)
        # Check
        result = self.poller._redis_connexion.redis_zrangebyscore("DATAS",'-inf','+inf')
        self.assertEqual(result, ['oldData', 'newData'])
        # Clear old data only
        self.poller.rediscleanDataExpired()
        # Check TimeStamp and DATAS
        result = self.poller._redis_connexion.redis_zrangebyscore("TimeStamp",'-inf','+inf')
        self.assertEqual(result, [nowTimestamp])
        result = self.poller._redis_connexion.redis_zrangebyscore("DATAS",'-inf','+inf')
        self.assertEqual(result, ['newData'])

    def test_poller_pollerTimeToGo(self):
        now              = time.strftime("%Y %m %d %H:%M", time.localtime())
        nowTimestamp     = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M')) # "%.0f" % supprime le .0 aprés le
        # Init
        self.poller._poller_time            = 60
        self.poller._plugins_refresh_time   = 300
        # At start refresh plugin not needed
        self.assertFalse(self.poller._need_refresh)
        # First start no file (need refresh and true)
        os.system("rm -f /tmp/poller_last.unittest")
        result = self.poller.pollerTimeToGo()
        self.assertTrue(result)
        self.assertTrue(self.poller._need_refresh)
        # Make corrupt /tmp/poller_last.unittest
        os.system(":>/tmp/poller_last.unittest")
        result = self.poller.pollerTimeToGo()
        self.assertTrue(result)
        self.assertTrue(self.poller._need_refresh)
        # Try to run quick poll (too soon)
        result = self.poller.pollerTimeToGo()
        self.assertFalse(result)
        self.assertFalse(self.poller._need_refresh)
        # change time in file for poller only, no refresh
        os.system("echo '"+str(int(nowTimestamp)-60)+" "+nowTimestamp+"' >/tmp/poller_last.unittest")
        result = self.poller.pollerTimeToGo()
        self.assertTrue(result)
        self.assertFalse(self.poller._need_refresh)
        # change time in file for poller and refresh
        os.system("echo '"+str(int(nowTimestamp)-60)+" "+str(int(nowTimestamp)-300)+"' >/tmp/poller_last.unittest")
        result = self.poller.pollerTimeToGo()
        self.assertTrue(result)
        self.assertTrue(self.poller._need_refresh)

    def test_poller_writeInfo(self):
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        self.poller._redis_connexion = self.poller.redisStartConnexion()
        # Test good values 2 plugins
        result = self.poller.writeInfo([{'Plugin':"foo", },{'Plugin':"bar"}])
        self.assertEquals(result,['foo', 'bar'])
        result = self.poller._redis_connexion.redis_hkeys("INFOS")
        self.assertEquals(result, ['foo', 'bar'])
        result = self.poller._redis_connexion.redis_hget("INFOS","foo")
        self.assertEquals(result, '{"Plugin": "foo"}') # (json string)
        # Test with empty value
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        result = self.poller.writeInfo([])
        self.assertEquals(result,[])
        result = self.poller._redis_connexion.redis_hkeys("INFOS")
        self.assertEquals(result, [])
        # Good value without plugin name
        self.poller.writeInfo([{'Title':"foo", }])
        result = self.poller._redis_connexion.redis_hkeys("INFOS")
        self.assertEquals(result, [])

    def test_poller_cleanInfo(self):
        self.poller._redis_connexion = self.poller.redisStartConnexion()
        pollerRedis = self.poller._redis_connexion
        # No data before (dont delete no data after)
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        self.poller.cleanInfo([{'Plugin':"foo", },{'Plugin':"bar"}])
        result = pollerRedis.redis_hkeys("INFOS")
        self.assertEquals(result, [])
        # 2 data before and same data now
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        pollerRedis.redis_hset("INFOS",'foo','foo')
        pollerRedis.redis_hset("INFOS",'bar','bar')
        self.poller.cleanInfo(["foo","bar"])
        result = pollerRedis.redis_hkeys("INFOS")
        self.assertEquals(result, ['foo', 'bar'])
        # 2 data before and only one now
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        pollerRedis.redis_hset("INFOS",'foo','foo')
        pollerRedis.redis_hset("INFOS",'bar','bar')
        self.poller.cleanInfo(["foo"])
        result = pollerRedis.redis_hkeys("INFOS")
        self.assertEquals(result, ['foo'])
        # 2 data before, delete one and add a new
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        pollerRedis.redis_hset("INFOS",'foo','foo')
        pollerRedis.redis_hset("INFOS",'bar','bar')
        self.poller.cleanInfo(["foo","gnu"])
        result = pollerRedis.redis_hkeys("INFOS")
        self.assertEquals(result, ['foo'])

    def test_poller_writeData(self):
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        self.poller._redis_connexion = self.poller.redisStartConnexion()
        # set Empty value
        self.poller.writeData([])
        result = self.poller._redis_connexion.redis_zrangebyscore("DATAS", '-inf','+inf')
        self.assertEquals(result, [])
        result = self.poller._redis_connexion.redis_zrangebyscore("TimeStamp", '-inf','+inf')
        self.assertEquals(result, [])
        # set good value
        self.poller.writeData([{"TimeStamp": "1328624580", "Values": {"entropy": "146"}, "Plugin": "entropy"},
                                {"TimeStamp": "1328624760", "Values": {"load": "0.00"}, "Plugin": "load"}])
        result = self.poller._redis_connexion.redis_zrangebyscore("DATAS", '-inf','+inf')
        self.assertEquals(result, ['{"TimeStamp": "1328624580", "Values": {"entropy": "146"}, "Plugin": "entropy"}',
                                   '{"TimeStamp": "1328624760", "Values": {"load": "0.00"}, "Plugin": "load"}'])
        result = self.poller._redis_connexion.redis_zrangebyscore("TimeStamp", '-inf','+inf')
        self.assertEquals(result, ['1328624580', '1328624760'])
        # send value without Plugin name
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        self.poller.writeData([{"TimeStamp": "1328624580", "Values": {"entropy": "146"}}])
        result = self.poller._redis_connexion.redis_zrangebyscore("DATAS", '-inf','+inf')
        self.assertEquals(result, [])
        result = self.poller._redis_connexion.redis_zrangebyscore("TimeStamp", '-inf','+inf')
        self.assertEquals(result, [])
        # set good value but non integer timestamp
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        self.poller.writeData([{"TimeStamp": "error", "Plugin": "entropy"}])
        result = self.poller._redis_connexion.redis_zrangebyscore("DATAS", '-inf','+inf')
        self.assertEquals(result, [])
        result = self.poller._redis_connexion.redis_zrangebyscore("TimeStamp", '-inf','+inf')
        self.assertEquals(result, [])


    def test_poller_redisStartConnexion(self):
        # Connect with 0
        self.poller._redis_db = 0
        zeroConnect = self.poller.redisStartConnexion()
        zeroConnect.redis_hset("DB","foo","bar0")
        # Connect with 1
        self.poller._redis_db = 1
        oneConnect = self.poller.redisStartConnexion()
        oneConnect.redis_hset("DB","foo","bar1")
        # Check
        result = zeroConnect.redis_hget("DB","foo")
        self.assertEquals(result, "bar0")
        result = oneConnect.redis_hget("DB","foo")
        self.assertEquals(result, "bar1")

