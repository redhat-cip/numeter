from login import Login_TestCase
from storage import Storage_TestCase
from browsing import Index_TestCase, Multiviews_TestCase, Configuration_TestCase
from management import Manage_User_TestCase, Manage_Storage_TestCase

def suite():
    import unittest
    TEST_CASES = (
        'core.tests.login',
        'core.tests.storage',
        'core.tests.browsing',
        'core.tests.management',
    )
    suite = unittest.TestSuite()
    for t in TEST_CASES :
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite
