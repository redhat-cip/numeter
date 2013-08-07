# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../../common'))
from myRedisConnect import myRedisConnect
class FakeRedis(myRedisConnect):
    def __init__(self, *args, **kwargs):
        self._error=False
        self.hset_data = self.init_hset()
        self.zadd_data = self.init_zadd()

    def init_hset(self):
        return {}

    def init_zadd(self):
        return {}

    def redis_zadd(self, key, value, score, *args, **kwargs):
        if not key in self.zadd_data:
            self.zadd_data[key] = {}
        if not score in self.zadd_data[key]:
            self.zadd_data[key][score] = []
        self.zadd_data[key][score].append(value)

    def redis_hset(self, name, key, value, *args, **kwargs):
        if not name in self.hset_data:
            self.hset_data[name] = {}
        self.hset_data[name][key] = value

    def redis_hdel(self, name, key, *args, **kwargs):
        del self.hset_data[name][key]

    def redis_hvals(self, name, *args, **kwargs):
        try:
            return [ value for value in self.hset_data['HOSTS'].itervalues() ]
        except:
            return []

    def redis_hkeys(self, name, *args, **kwargs):
        if name in self.hset_data:
            return self.hset_data[name].keys()
        else:
            return None

    def redis_zremrangebyscore(self, name, min, max, *args, **kwargs):
        all_items = self.zadd_data.get(name, {})
        removed = 0
        if min == '-inf' or min == '+inf':
            min = float(min)
        if max == '-inf' or max == '+inf':
            max = float(max)
        for score in all_items.keys():
            if min <= score <= max:
                del all_items[score]
                removed += 1
        self.zadd_data[name] = all_items
        return removed

    def get_and_flush_hset(self):
        data = self.hset_data
        self.hset_data = {}
        return data

    def get_and_flush_zadd(self):
        data = self.zadd_data
        self.zadd_data = {}
        return data

