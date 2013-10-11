# -*- coding: utf-8 -*-

raise Exception("Rewrite in progress")

import unittest2 as unittest
from redis_Unittest import RedisTestCase
from poller_Unittest import PollerTestCase
from mastertest_Unittest import MasterTestCase
from storage_Unittest import StorageTestCase
#from connection_pool import ConnectionPoolTestCase
#from pipeline import PipelineTestCase
#from lock import LockTestCase

#use_hiredis = False
#try:
#    import hiredis
#    use_hiredis = True
#except ImportError:
#    pass


def all_tests():
    suite = unittest.TestSuite()
    # Redis
    suite.addTest(unittest.makeSuite(RedisTestCase))
    # Poller
    suite.addTest(unittest.makeSuite(PollerTestCase))
    # Storage
    suite.addTest(unittest.makeSuite(StorageTestCase))
    # Master test with all /!\ Need munin-node and redis
    suite.addTest(unittest.makeSuite(MasterTestCase))
    return suite

#self.assertRaises(TypeError, adder, 33, 'a string')


