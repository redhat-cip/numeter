from login import Login_TestCase
from storage import Storage_TestCase
from browsing import Index_TestCase, Multiviews_TestCase, Configuration_TestCase

def suite():
    import unittest
    TEST_CASES = (
        'core.tests.login',
        # 'core.tests.storage',
        'core.tests.browsing',
    )
    suite = unittest.TestSuite()
    for t in TEST_CASES :
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite
