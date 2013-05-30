#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis




#
# Redis
#
class myRedisConnect:
    """Frontend redis avec try sur les get"""
    def __init__(self,host="127.0.0.1",port=6379,socket_timeout=2,password=None,db=0):
#        print "-INIT"
        self._error     = False
        self._host      = host
        self._port      = port
        self._db        = db
        self.password   = password
        self._socket_timeout = socket_timeout
        self.redis_connect()


    def redis_connect(self):
        self.conn=None
#        print "-Connect"
        try:
            self._conn=redis.Redis(host=self._host, port=self._port, db=self._db, socket_timeout=self._socket_timeout, password=self.password)
            self._conn.ping()
        except redis.exceptions.ConnectionError, e:
            print "Redis connexion - ERROR"
            self._error = True
        except redis.exceptions.ResponseError, e:
            print "Redis connexion - ping() ResponseError Try to check the password"
            self._error = True

    def redis_zcount(self,name,valmin,valmax):
        try:
            return self._conn.zcount(name,valmin,valmax)
        except redis.exceptions.ConnectionError, e:
            print "ZCOUNT - error redis"

    def redis_hlen(self,name):
        try:
            return self._conn.hlen(name)
        except redis.exceptions.ConnectionError, e:
            print "HLEN - error redis"

    def redis_set(self,key,value):
#        print "-SET "+key+", "+value
        try:
            self._conn.set(key, value)   
        except redis.exceptions.ConnectionError, e:
            print "SET - error redis"

    def redis_get(self,key):
#        print "GET "+key
        try:
            return self._conn.get(key)
        except redis.exceptions.ConnectionError, e:
            print "GET - error redis"

    def redis_keys(self,key):
        try:
            return self._conn.keys(key)
        except redis.exceptions.ConnectionError, e:
            print "KEYS - error redis"

    def redis_info(self):
        try:
            return self._conn.info()
        except redis.exceptions.ConnectionError, e:
            print "INFO - error redis"

    def redis_zadd(self,name,value,score):
#        print "-ZADD "+name+", "+str(score)
#        print "-ZADD "+name+", "+str(score)+", "+value
        try:
            self._conn.zadd(name, value, score)   
            # Version > 2.0.0-1 -> 2.4.9-1
#            self._conn.zadd(name, **{value: key}) # For future deprecated https://github.com/andymccurdy/redis-py/pull/164
        except redis.exceptions.ConnectionError, e:
            print "ZADD - error redis"

    def redis_zrangebyscore(self,name,valmin,valmax,start=None, num=None):
#        print "-ZrangeByScore "+name+", "+valmin+", "+valmax
        try:
            result=self._conn.zrangebyscore(name, valmin, valmax,start=start, num=num)
            if not result:
                result=[]
            return result
        except redis.exceptions.ConnectionError, e:
            print "ZRANGEBYSCORE - error redis"

    def redis_zremrangebyscore(self,name,valmin,valmax):
#        print "-ZRemRangeByScore "+name+", "+valmin+", "+valmax
        try:
            return self._conn.zremrangebyscore(name, valmin, valmax)   
        except redis.exceptions.ConnectionError, e:
            print "ZREMRANGEBYSCORE - error redis"

    def redis_hset(self,name,key,value):
        try:
            self._conn.hset(name, key, value)   
        except redis.exceptions.ConnectionError, e:
            print "HSET - error redis"

    def redis_hmset(self,name,mapping):
#        mapping = {'a': '1', 'b': '2', 'c': '3'}
        try:
            self._conn.hmset(name, mapping)   
        except redis.exceptions.ConnectionError, e:
            print "HMSET - error redis"

    def redis_hmget(self,name,key):
#       [Key,key,key]
        try:
            return self._conn.hmget(name,key)   
        except redis.exceptions.ConnectionError, e:
            print "HMGET - error redis"

    def redis_hget(self,name,key):
        try:
            return self._conn.hget(name,key)   
        except redis.exceptions.ConnectionError, e:
            print "HGET - error redis"

    def redis_hexists(self,name,key):
        # True / False
        try:
            return self._conn.hexists(name,key)   
        except redis.exceptions.ConnectionError, e:
            print "HEXISTS - error redis"


    def redis_hdel(self,name,key):
        try:
            return self._conn.hdel(name,key)   
        except redis.exceptions.ConnectionError, e:
            print "HDEL - error redis"

    def redis_hkeys(self,name):
        try:
            return self._conn.hkeys(name)   
        except redis.exceptions.ConnectionError, e:
            print "HKEYS - error redis"

    def redis_hvals(self,name):
        try:
            return self._conn.hvals(name)   
        except redis.exceptions.ConnectionError, e:
            print "HVALS - error redis"

    def redis_hgetall(self,name):
        try:
            return self._conn.hgetall(name)   
        except redis.exceptions.ConnectionError, e:
            print "HGETALL - error redis"








