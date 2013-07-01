# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../../common'))
from myRedisConnect import myRedisConnect

class FakeRedis(myRedisConnect):

    def __init__(self):
        self._error=False
        self.zadd_data={}

    def redis_zadd(self, *args, **kwargs):
        key = args[0]
        value = args[1]
        score = args[2]
        if not key in self.zadd_data:
            self.zadd_data[key] = {}
        if not score in self.zadd_data[key]:
            self.zadd_data[key][score] = []
        self.zadd_data[key][score].append(value)

    def get_and_flush_zadd(self):
        data = self.zadd_data
        self.zadd_data = {}
        return data
