from profile import Profile_Test
from user import User_Test
from group import Group_Test
from storage import Storage_Test
from host import Host_Test
from plugin import Plugin_Test
from source import Source_Test
from view import View_Test
from multiview import Multiview_Test
from event import Event_Test


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
        'configuration.tests.event',
    )
    suite = unittest.TestSuite()
    for t in TEST_CASES:
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite
