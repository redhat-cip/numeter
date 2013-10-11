from login import Login_Test
from perms import Perms_Test
from storage import Storage_Test, Storage_Manager_Test
from host import Host_Test
from plugin import Plugin_Manager_Test, Plugin_Test
from source import Source_Manager_Test, Source_Test
from browsing import Index_Test
from management import Manage_User_Test, Manage_Storage_Test, Manage_Repair_Test
from commands.storage import Cmd_Storage_List_Test
from hosttree import Hosttree_Test
from group_restriction import Access_Test
from mediafield import MediaField_Test

def suite():
    import unittest
    TEST_CASES = (
        'core.tests.management',
        'core.tests.perms',
        'core.tests.mediafield',
        'core.tests.login',
        'core.tests.group_restriction',
        'core.tests.browsing',
        'core.tests.hosttree',
        'core.tests.storage',
        'core.tests.host',
        'core.tests.plugin',
        'core.tests.source',
    )
    suite = unittest.TestSuite()
    for t in TEST_CASES:
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite
