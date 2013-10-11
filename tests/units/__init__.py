# -*- coding: utf-8 -*-

import unittest2 as unittest
from poller_Unittest import PollerTestCase
from poller_MuninModuleUnittest import PollerMuninModuleTestCase
from storage_Unittest import StorageTestCase
from cachelastvalue_Unittest import CacheLastValueTestCase
from storeandforward_Unittest import StoreAndForwardTestCase
from poller_munin_connectUnittest import PollerMuninConnectTestCase

def all_tests():
    suite = unittest.TestSuite()
    ## Poller
    suite.addTest(unittest.makeSuite(PollerMuninModuleTestCase))
    suite.addTest(unittest.makeSuite(PollerTestCase))
    suite.addTest(unittest.makeSuite(CacheLastValueTestCase))
    suite.addTest(unittest.makeSuite(StoreAndForwardTestCase))
    suite.addTest(unittest.makeSuite(PollerMuninConnectTestCase))
    # Storage
    suite.addTest(unittest.makeSuite(StorageTestCase))
    return suite
