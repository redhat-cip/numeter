from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from core.models import User


class Profile_TestCase(TestCase):
    fixtures = ['test_users.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')
        self.admin = User.objects.get(pk=1)
        self.user = User.objects.get(pk=2)

    def test_index(self):
        """Simple get."""
        url = reverse('configuration')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_change_username(self):
        """Change username and test if changed."""
        url = self.admin.get_update_url()
        r = self.c.post(url, {'username': 'toto', 'graph_lib': ['dygraph-combined.js']})
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        self.assertTrue(User.objects.filter(username='toto').exists(), "New username not foundable.")

    def test_change_own_password(self):
        """Test if a user try to change his password."""
        # Disconnect to login as simple user
        self.c.logout()
        self.c.login(username='Client', password='pass')
        # Sent POST
        url = self.user.get_update_password_url()
        POST = {'old':'pass','new_1':'root','new_2':'root'}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        self.user = User.objects.get(pk=2)
        self.assertTrue(self.user.check_password('root'), "Password doesn't change.")

    def test_admin_change_password(self):
        """Test if admin can change other user's password."""
        url = self.user.get_update_password_url()
        POST = {'old':'pass','new_1':'root','new_2':'root'}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        self.user = User.objects.get(pk=2)
        self.assertTrue(self.user.check_password('root'), "New password checking failed.")

    def test_forbidden_change_password(self):
        """Test if user can change other user's password."""
        # Disconnect to login as simple user
        self.c.logout()
        self.c.login(username='Client', password='pass')
        # Sent POST
        url = self.admin.get_update_password_url()
        POST = {'old':'toto','new_1':'root','new_2':'root'}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)
        self.assertFalse(self.user.check_password('root'), "Third user can change password.")

