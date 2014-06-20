"""
Profile modal tests module.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from core.models import User
from core.tests.utils import set_users, set_clients


class Profile_Test(TestCase):
    """Tests user's profile modal."""
    @set_users()
    @set_clients()
    def setUp(self):
        pass

    def test_index(self):
        """Get modal."""
        url = reverse('profile')
        r = self.admin_client.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_change_own_password(self):
        """Test if a user try to change his password."""
        # Sent POST
        url = self.user.get_update_password_url()
        POST = {'old':'toto', 'new_1':'root', 'new_2':'root'}
        r = self.user_client.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        self.user = User.objects.get(pk=self.user.pk)
        self.assertTrue(self.user.check_password('root'), "Password doesn't change.")

    def test_admin_change_password(self):
        """Test if admin can change other user's password."""
        url = self.admin.get_update_password_url()
        POST = {'old':'toto', 'new_1':'root', 'new_2':'root'}
        r = self.admin_client.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        self.admin = User.objects.get(pk=self.admin.pk)
        self.assertTrue(self.admin.check_password('root'), "New password checking failed.")

    def test_forbidden_change_password(self):
        """Test if user can change other user's password."""
        # Sent POST
        url = self.admin.get_update_password_url()
        POST = {'old':'toto', 'new_1':'root', 'new_2':'root'}
        r = self.user_client.post(url, POST)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)
        self.assertFalse(self.user.check_password('root'), "Third user can change password.")
