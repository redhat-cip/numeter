from view import View_TestCase
from event import Event_TestCase
from customize.source import Customize_Source_TestCase
from customize.view import Customize_View_TestCase
from customize.multiview import Customize_Multiview_TestCase
from customize.event import Customize_Event_TestCase

def suite():
    import unittest
    TEST_CASES = (
        'multiviews.tests.view',
        'multiviews.tests.event',
        'multiviews.tests.customize.source',
        'multiviews.tests.customize.view',
        'multiviews.tests.customize.multiview',
        'multiviews.tests.customize.event',
    )
    suite = unittest.TestSuite()
    for t in TEST_CASES:
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite
