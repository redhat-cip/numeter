from plugin import Plugin_Manager_TestCase, Plugin_TestCase
from data_source import Data_Source_TestCase
from browsing import Configuration_Plugin_TestCase, Configuration_Source_TestCase, Configuration_View_TestCase, Configuration_Multiview_TestCase

def suite():
    import unittest
    TEST_CASES = (
        'multiviews.tests.plugin',
        'multiviews.tests.data_source',
        'multiviews.tests.browsing',
    )
    suite = unittest.TestSuite()
    for t in TEST_CASES:
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite

