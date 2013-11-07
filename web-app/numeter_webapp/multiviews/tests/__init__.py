from view import View_Test
from skeleton import Skeleton_Test
from event import Event_Test
from customize.source import Customize_Source_Test
from customize.view import Customize_View_Test
from customize.multiview import Customize_Multiview_Test
from customize.event import Customize_Event_Test
from commands.view import Cmd_View_List_Test, Cmd_View_Add_Test, Cmd_View_Del_Test, Cmd_View_Mod_Test
from commands.skeleton import Cmd_Skeleton_List_Test, Cmd_Skeleton_Add_Test, Cmd_Skeleton_Del_Test, Cmd_Skeleton_Mod_Test, Cmd_Skeleton_Create_View_Test

def suite():
    import unittest
    TEST_CASES = (
        'multiviews.tests.commands.view',
        'multiviews.tests.commands.skeleton',
        'multiviews.tests.view',
        'multiviews.tests.skeleton',
#        'multiviews.tests.event',
        'multiviews.tests.customize.source',
        'multiviews.tests.customize.view',
        'multiviews.tests.customize.multiview',
#        'multiviews.tests.customize.event',
    )
    suite = unittest.TestSuite()
    for t in TEST_CASES:
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite
