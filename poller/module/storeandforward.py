#!/usr/bin/env python

import json
import logging

class StoreAndForward(object):
    def __init__(self, cache_file='/dev/shm/store_and_forward.json', logger='StoreAndForward'):
        self._cache_file = cache_file
        self._cache = []
        self.error = ''
        self._logger = logging.getLogger(logger)

    def add_message(self, msgType, plugin, msgContent):
        self._cache.append({
                            'msgType': msgType,
                            'plugin': plugin,
                            'msgContent': msgContent,
                          })

    def load_cache(self):
        try:
            with open(self._cache_file, 'r') as f:
                self._cache = json.load(f)
        except IOError, e:
            self._logger.warning('Load cache IOError: %s Use default cache []' %e)

    def dump_cache(self):
        try:
            with open(self._cache_file, 'w') as f:
                json.dump(self._cache, f)
        except IOError, e:
            self._logger.critical("Dump cache IOError: %s Can't write cache" %e)

    def consume(self):
        while self._cache:
            yield self._cache.pop()

## Init logging level
#logging.getLogger('StoreAndForward').setLevel(logging.CRITICAL)
#
## Add handler for debug
#logging.getLogger('StoreAndForward').setLevel(logging.INFO)
#logging.getLogger('StoreAndForward').addHandler(logging.StreamHandler())
#
#cache = StoreAndForward(cache_file='./sandbox/cache_storeandforward.json')
#cache.load_cache()
#
#from time import time
#cache.add_message('DATA', 'munin.if_eth0.up', '{%s content}' % time())
#
#
#for message in cache.consume():
#    print message
#
#cache.dump_cache()
##module.plugin.value : timestamp / value
