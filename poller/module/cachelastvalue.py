#!/usr/bin/env python

import json
import logging

class CacheLastValue(object):
    def __init__(self, cache_file='/dev/shm/cache_last_value.json', logger='CacheLastValue'):
        self._cache_file = cache_file
        self._cache = {}
        self.error = ''
        self._logger = logging.getLogger(logger)

    def load_cache(self):
        try:
            with open(self._cache_file, 'r') as f:
                self._cache = json.load(f)
        except IOError, e:
            self._logger.warning('%s - Load cache IOError: %s Use default cache {}'
                                    % (__name__, e))

    def dump_cache(self):
        try:
            with open(self._cache_file, 'w') as f:
                json.dump(self._cache, f)
        except IOError, e:
            self._logger.critical("%s - Dump cache IOError: %s Can't write cache"
                                    % (__name__, e))

    def save_value(self, key, timestamp, value):
        self._cache[key] = {'timestamp': timestamp,
                            'value': value}

    def get_value(self, key):
        return self._cache.get(key,None)
