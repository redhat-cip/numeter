"""
rest tests module. Allow to launch a single TestCase or all.
"""

from login import Login_Test
from user import User_GET_list_Test, User_GET_detail_Test, User_POST_Test, User_DELETE_Test, User_PATCH_Test, User_POST_set_password_Test


def suite():
    import unittest
    TEST_CASES = (
        'rest.tests.login',
        'rest.tests.user',
    )
    suite = unittest.TestSuite()
    for t in TEST_CASES:
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite
