"""
User model tests module.
"""

from django.test import LiveServerTestCase
from core.models import User
from core.tests.utils import set_users


class User_Manager_user_filter_Test(LiveServerTestCase):
    """
    Test filter user by his users and groups attributes.
    """
    @set_users()
    def setUp(self):
        pass

    def test_grant_to_super_user(self):
        """Superuser access to every users."""
        users = User.objects.user_filter(self.admin)
        self.assertEqual(users.count(), User.objects.count(), "Superuser can't access to all users")

    def test_grant_to_simple_user_with_his_group(self):
        """User access to his own user."""
        users = User.objects.user_filter(self.user)
        self.assertEqual(users.count(), 1, "User can't access to his group")


class User_Test(LiveServerTestCase):
    def setUp(self):
        pass
