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

    def redis_hget(self, name, key):
        return self.hset_data.get(name, {}).get(key)

    def redis_hgetall(self,name):
        return self.hset_data.get(name,{})

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

    def redis_zrangebyscore(self, name, min, max, start=None, num=None, withscores=False):
        if (start is not None and num is None) or \
                (num is not None and start is None):
            raise redis.RedisError("``start`` and ``num`` must both "
                                   "be specified")
        all_items = self.zadd_data.get(name, {})
        matches = []
        for score in all_items.keys():
            print '%s <= %s <= %s value %s' % (min, score, max, all_items[score])
            # Float fot -inf and +inf and other mistake
            matched = False
            if min.startswith('(') and max.startswith('('):
                if float(min[1:]) < float(score) < float(max[1:]):
                    matched = True
            elif min.startswith('('):
                if float(min[1:]) < float(score) <= float(max):
                    matched = True
            elif max.startswith('('):
                if float(min) <= float(score) < float(max[1:]):
                    matched = True
            else:
                if float(min) <= float(score) <= float(max):
                    matched = True
            if matched:
                print 'OK...'
                matches.extend(all_items[score])
        if start is not None:
            matches = matches[start:start + num]
        return matches

    def redis_zremrangebyscore(self, name, min, max, *args, **kwargs):
        all_items = self.zadd_data.get(name, {})
        removed = 0
        for score in all_items.keys():
            # Float fot -inf and +inf and other mistake
            matched = False
            if min.startswith('(') and max.startswith('('):
                if float(min[1:]) < float(score) < float(max[1:]):
                    matched = True
            elif min.startswith('('):
                if float(min[1:]) < float(score) <= float(max):
                    matched = True
            elif max.startswith('('):
                if float(min) <= float(score) < float(max[1:]):
                    matched = True
            else:
                if float(min) <= float(score) <= float(max):
                    matched = True
            if matched:
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

