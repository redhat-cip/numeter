from wild_storage import Wild_Storage_Test
from user import User_Test, User_Forbidden_Test
from group import Group_Test, Group_Forbidden_Test


def suite():
    import unittest
    TEST_CASES = (
      'rest.tests.wild_storage',
      'rest.tests.user',
      'rest.tests.group',
    )
    suite = unittest.TestSuite()
    for t in TEST_CASES:
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite
