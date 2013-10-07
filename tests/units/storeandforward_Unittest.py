#!/usr/bin/env python
import unittest
import os, sys
import mock

myPath = os.path.abspath(os.path.dirname(__file__))

import base as test_base

from numeter.poller.storeandforward import StoreAndForward

class StoreAndForwardTestCase(test_base.TestCase):

    def setUp(self):
        super(StoreAndForwardTestCase, self).setUp()
        self.store = StoreAndForward()

    def tearDown(self):
        super(StoreAndForwardTestCase, self).tearDown()

    def test_dump_cache(self):
        # dump need write _cache default {}
        with mock.patch('__builtin__.open', mock.mock_open(), create=True) as file_mock:
            handle = file_mock()
            self.store._dump_cache()
            handle.write.assert_called_once_with('[]')

    def test_load_cache(self):
        # load cache from file
        with mock.patch('__builtin__.open', mock.mock_open(), create=True) as file_mock:
            file_mock.return_value.read.return_value = '["foo", "bar"]'
            self.store._load_cache()
            self.assertEquals(self.store._cache, ['foo', 'bar'])

    def test_add_message(self):
        # save message
        msgType = 'foo'; plugin = 'bar'; msgContent = { 'bla': 'moo' }
        self.store.add_message(msgType, plugin, msgContent)
        self.assertEquals(self.store._cache, [{'msgContent': msgContent,
                                               'msgType': msgType,
                                               'plugin': plugin}])

    def test_consume(self):
        # Empty storage
        self.store._cache = [1, 2]
        self.store.consume().next()
        self.assertEquals(self.store._cache, [1])
        self.store.consume().next()
        self.assertEquals(self.store._cache, [])

