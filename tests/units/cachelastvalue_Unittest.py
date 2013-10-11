#!/usr/bin/env python
import unittest
import os, sys
import mock

from numeter.poller.cachelastvalue import CacheLastValue

import base as test_base


class CacheLastValueTestCase(test_base.TestCase):

    def setUp(self):
        super(CacheLastValueTestCase, self).setUp()
        self.cache = CacheLastValue()

    def tearDown(self):
        super(CacheLastValueTestCase, self).tearDown()

    def test_dump_cache(self):
        # dump need write _cache default {}
        with mock.patch('__builtin__.open', mock.mock_open(), create=True) as file_mock:
            handle = file_mock()
            self.cache._dump_cache()
            handle.write.assert_called_once_with('{}')

    def test_load_cache(self):
        # load cache from file
        with mock.patch('__builtin__.open', mock.mock_open(), create=True) as file_mock:
            file_mock.return_value.read.return_value = '{"foo": "bar"}'
            self.cache._load_cache()
            self.assertEquals(self.cache._cache, {'foo':'bar'})

    def test_save_value(self):
        # save value
        key = 'foo'; timestamp = '000000000'; value = 42;
        self.cache.save_value(key, timestamp, value)
        self.assertEquals(self.cache._cache, {key: {'timestamp': timestamp,
                                                    'value': value}})

    def test_get_value(self):
        self.cache._cache = {'foo': 'bar'}
        result = self.cache.get_value('foo')
        self.assertEquals(result, 'bar')

