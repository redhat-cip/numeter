"""
core tests module. Allow to launch a single TestCase or all.
"""

from login import Login_Test
from perms import Perms_Test
from storage import Storage_Test, Storage_Manager_Test, Storage_Error_Test
from host import Host_Test, Host_Manager_user_filter_Test
from plugin import Plugin_Manager_Test, Plugin_Test, Plugin_Manager_user_filter_Test
from source import Source_Manager_Test, Source_Test, Source_Manager_user_filter_Test
from browsing import Index_Test
from commands.group import Cmd_Group_List_Test, Cmd_Group_Add_Test, Cmd_Group_Del_Test, Cmd_Group_Mod_Test, Cmd_Group_Hosts_Test
from commands.user import Cmd_User_List_Test, Cmd_User_Add_Test, Cmd_User_Del_Test, Cmd_User_Mod_Test
from commands.storage import Cmd_Storage_List_Test, Cmd_Storage_Add_Test, Cmd_Storage_Del_Test, Cmd_Storage_Mod_Test
from commands.host import Cmd_Host_List_Test, Cmd_Host_Add_Test, Cmd_Host_Del_Test, Cmd_Host_Mod_Test, Cmd_Host_Repair_Test
from commands.plugin import Cmd_Plugin_List_Test, Cmd_Plugin_Add_Test, Cmd_Plugin_Del_Test
from commands.source import Cmd_Source_List_Test, Cmd_Source_Add_Test, Cmd_Source_Del_Test
from commands.populate import Cmd_Populate_Test
from profile import Profile_Test
from hosttree import Hosttree_Test
from group_restriction import Access_Test
from mediafield import MediaField_Test


def suite():
    import unittest
    TEST_CASES = (
        'core.tests.commands.group',
        'core.tests.commands.user',
        'core.tests.commands.storage',
        'core.tests.commands.host',
        'core.tests.commands.plugin',
        'core.tests.commands.source',
        'core.tests.perms',
        'core.tests.mediafield',
        'core.tests.login',
        'core.tests.group_restriction',
        'core.tests.browsing',
        'core.tests.profile',
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
