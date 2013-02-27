#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys

myPath = os.path.abspath(os.path.dirname(__file__))

sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../common/module'))
from myRedisConnect import *

class RedisTestCase(unittest.TestCase):

    def get_init(self):
        # Redis connexion with no error
        self._redis_connexion = myRedisConnect(host="127.0.0.1", port=8888, password="password",db=0)
        self.assertFalse(self._redis_connexion._error)

    def setUp(self):
        os.system("kill -9 $(cat /var/run/redis/redis-unittest.pid 2>/dev/null) 2>/dev/null")
        os.system('kill -9 $(pgrep -f "redis-server '+myPath+'/redis_unittest.conf")')
        os.system("redis-server "+myPath+"/redis_unittest.conf")
        os.system("while ! netstat -laputn | grep 8888 > /dev/null; do true; done ")
        os.system("redis-cli -a password -p 8888 ping >/dev/null")
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        self.get_init()


    def tearDown(self):
        os.system("kill -9 $(cat /var/run/redis/redis-unittest.pid)")
        os.system('kill -9 $(pgrep -f "redis-server '+myPath+'/redis_unittest.conf")')


    def test_redis_db(self):
        # Test connect db 0, 1 and default
        redis_dbDefault = myRedisConnect(host="127.0.0.1", port=8888, password="password",db=None)
        redis_db0 = myRedisConnect(host="127.0.0.1", port=8888, password="password",db=0)
        redis_db1 = myRedisConnect(host="127.0.0.1", port=8888, password="password",db=1)
        # Set and get value in 0
        redis_db0.redis_set("foo","bar0")
        self.assertEqual(redis_db0.redis_get("foo"), "bar0")
        # Set value in 1 with same key
        redis_db1.redis_set("foo","bar1")
        # Get value in 0 and default 
        self.assertEqual(redis_db0.redis_get("foo"), "bar0")
        self.assertEqual(redis_dbDefault.redis_get("foo"), "bar0")
        # Get value in 1
        self.assertEqual(redis_db1.redis_get("foo"), "bar1")



    def test_redis_setGet(self):
        # Set and get value
        self._redis_connexion.redis_set("foo","bar")
        self.assertEqual(self._redis_connexion.redis_get("foo"), "bar")

    def test_redis_zaddZrangeZrem(self):
        # zadd value
        self._redis_connexion.redis_zadd("ZFOO","bar1",1)
        self._redis_connexion.redis_zadd("ZFOO","bar2",2)
        self._redis_connexion.redis_zadd("ZFOO","bar3",3)
        # zrange 
        result = self._redis_connexion.redis_zrangebyscore("ZFOO",'-inf','+inf',start=None, num=None)
        self.assertEqual(result, ['bar1', 'bar2', 'bar3'])
        result = self._redis_connexion.redis_zrangebyscore("ZFOO",'1','2',start=None, num=None)
        self.assertEqual(result, ['bar1', 'bar2'])
        result = self._redis_connexion.redis_zrangebyscore("ZFOO",'(1','2')
        self.assertEqual(result, ['bar2'])
        result = self._redis_connexion.redis_zrangebyscore("ZFOO",'(1','(2')
        self.assertEqual(result, [])
        result = self._redis_connexion.redis_zrangebyscore("ZFOO",'1','3',start=0, num=2)
        self.assertEqual(result, ['bar1', 'bar2'])
        result = self._redis_connexion.redis_zrangebyscore("ZFOO",'1','3',start=1, num=2)
        self.assertEqual(result, ['bar2', 'bar3'])
        result = self._redis_connexion.redis_zrangebyscore("ZFOO",'1','1')
        self.assertEqual(result, ['bar1'])
        # Zrem
        self._redis_connexion.redis_zremrangebyscore("ZFOO",'(1','2')
        result = self._redis_connexion.redis_zrangebyscore("ZFOO",'-inf','+inf')
        self.assertEqual(result, ['bar1', 'bar3'])
        self._redis_connexion.redis_zremrangebyscore("ZFOO",'2','3')
        result = self._redis_connexion.redis_zrangebyscore("ZFOO",'-inf','+inf')
        self.assertEqual(result, ['bar1'])
        self._redis_connexion.redis_zremrangebyscore("ZFOO",'(1','1')
        result = self._redis_connexion.redis_zrangebyscore("ZFOO",'-inf','+inf')
        self.assertEqual(result, ['bar1'])
        self._redis_connexion.redis_zremrangebyscore("ZFOO",'1','1')
        result = self._redis_connexion.redis_zrangebyscore("ZFOO",'-inf','+inf')
        self.assertEqual(result, [])


    def test_redis_hsetGetDelExists(self):
        # Hset
        self._redis_connexion.redis_hset("HFOO","kbar","vbar")
        result = self._redis_connexion.redis_hget("HFOO","kbar")
        self.assertEqual(result, "vbar")
        # Hdel
        self._redis_connexion.redis_hdel("HFOO","kbar")
        result = self._redis_connexion.redis_hget("HFOO","kbar")
        self.assertEqual(result, None)
        # Exist
        result = self._redis_connexion.redis_hexists("HFOO","kbar")
        self.assertEqual(result, False)
        self._redis_connexion.redis_hset("HFOO","kbar","vbar")
        result = self._redis_connexion.redis_hexists("HFOO","kbar")
        self.assertEqual(result, True)
        # Hget
        result = self._redis_connexion.redis_hget("HFOO","kbar")
        self.assertEqual(result, "vbar")

    def test_redis_hmsetMgetGetallKeysVals(self):
        # Hmset
        mapping = {'Kmbar1': 'Vmbar1', 'Kmbar2': 'Vmbar2', 'Kmbar3': 'Vmbar3'}
        self._redis_connexion.redis_hmset("HMFOO",mapping)
        # Hmget
        keys = ['Kmbar1','Kmbar2','Kmbar4']
        result = self._redis_connexion.redis_hmget("HMFOO",keys)
        self.assertEqual(result, ['Vmbar1','Vmbar2', None])
        #Hkeys
        result = self._redis_connexion.redis_hkeys("HMFOO")
        self.assertEqual(sorted(result), ['Kmbar1','Kmbar2','Kmbar3'])
        # Hvals
        result = self._redis_connexion.redis_hvals("HMFOO")
        self.assertEqual(sorted(result), ['Vmbar1', 'Vmbar2', 'Vmbar3'])
        # Hgetall
        result = self._redis_connexion.redis_hgetall("HMFOO")
        self.assertEqual(result, mapping)



















