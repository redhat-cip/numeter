from profile import Profile_TestCase
from user import User_TestCase
from group import Group_TestCase
from storage import Storage_TestCase
from host import Host_TestCase
from plugin import Plugin_TestCase
from source import Source_TestCase
from view import View_TestCase
from multiview import Multiview_TestCase

def suite():
    import unittest
    TEST_CASES = (
        'configuration.tests.profile',
        'configuration.tests.user',
        'configuration.tests.group',
        'configuration.tests.storage',
        'configuration.tests.host',
        'configuration.tests.plugin',
        'configuration.tests.source',
        'configuration.tests.view',
        'configuration.tests.multiview',
    )
    suite = unittest.TestSuite()
    for t in TEST_CASES:
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite
