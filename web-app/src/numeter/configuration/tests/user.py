from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from core.models import User


class User_TestCase(TestCase):
    fixtures = ['test_users.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def tearDown(self):
        User.objects.all().delete()

    def test_index(self):
        """Get users index."""
        url = reverse('user index')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_user_list(self):
        """Get users list."""
        url = reverse('user list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_superuser_list(self):
        """Get superuser list."""
        url = reverse('superuser list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a user."""
        url = reverse('user', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """
        Test to get user form.
        Simulate it in POST method.
        Test to get new user.
        """
        # Test to get form
        url = reverse('user add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test to add
        POST = { 'username': 'new test', 'password': 'toto', 'graph_lib': 'dygraph-combined.js' }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test to get
        u = User.objects.get(username='new test')
        url = reverse('user', args=[u.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test to login
        self.c.logout()
        r = self.c.login(username='new test', password='toto')
        self.assertTrue(r, "New user can't login.")

    def test_update(self):
        """
        Simulate a POST which change a user.
        Test to see if username changed.
        """
        # Test to update
        url = reverse('user update', args=[1])
        POST = { 'username': 'new test', 'graph_lib': ['dygraph-combined.js'] }
        r = self.c.post(url, POST) 
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test if updated
        user = User.objects.get(pk=1)
        self.assertEqual(user.username, 'new test', 'Username is not changed (%s).' % user.username)

    def test_delete(self):
        """
        Test to delete user and if can't get it.
        """
        # Test to delete
        url = reverse('user delete', args=[2])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test to get it
        url = reverse('user', args=[2])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)

