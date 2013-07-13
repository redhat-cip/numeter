"""
Tests which browsing into website with GET and POST methods.
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.models import User, Storage, Group


class Index_TestCase(TestCase):
    fixtures = ['test_users.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def test_index(self):
        """Simple get."""
        url = reverse('index')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_apropos(self):
        """Simple get."""
        url = reverse('apropos')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)


class Multiviews_TestCase(TestCase):
    fixtures = ['test_users.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def test_index(self):
        """Simple get."""
        url = reverse('multiviews')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)


class Configuration_Profile_TestCase(TestCase):
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
        r = self.c.post(url, {'username': 'toto', 'graph_lib': 1})
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        self.assertTrue(User.objects.filter(username='toto').exists(), "New username not foundable.")

    def test_change_own_password(self):
        """Test if a user try to change his password."""
        # Disconnect to login as simple user
        self.c.logout()
        self.c.login(username='user #1', password='toto')
        # Sent POST
        url = self.user.get_update_password_url()
        POST = {'old':'toto','new_1':'root','new_2':'root'}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        self.user = User.objects.get(pk=2)
        self.assertTrue(self.user.check_password('root'), "Password doesn't change.")

    def test_admin_change_password(self):
        """Test if admin can change other user's password."""
        url = self.user.get_update_password_url()
        POST = {'old':'toto','new_1':'root','new_2':'root'}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        self.user = User.objects.get(pk=2)
        self.assertTrue(self.user.check_password('root'), "New password checking failed.")

    def test_forbidden_change_password(self):
        """Test if user can change other user's password."""
        # Disconnect to login as simple user
        self.c.logout()
        self.c.login(username='user #1', password='toto')
        # Sent POST
        url = self.admin.get_update_password_url()
        POST = {'old':'toto','new_1':'root','new_2':'root'}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)
        self.assertFalse(self.user.check_password('root'), "Third user can change password.")


class Configuration_User_TestCase(TestCase):
    fixtures = ['test_users.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def tearDown(self):
        User.objects.all().delete()

    def test_index(self):
        """Simple get."""
        url = reverse('user index')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_list(self):
        """Simple get."""
        url = reverse('user list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_superuser_list(self):
        """Simple get."""
        url = reverse('superuser list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Simple get."""
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
        POST = { 'username': 'new test', 'graph_lib': 1 }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get
        url = reverse('user', args=[3])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """
        Simulate a POST which change a user.
        Test to see if username changed.
        """
        # Test to update
        url = reverse('user update', args=[1])
        POST = { 'username': 'new test', 'graph_lib': 1 }
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


class Configuration_Group_TestCase(TestCase):
    fixtures = ['test_users.json', 'test_groups.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def tearDown(self):
        Group.objects.all().delete()

    def test_list(self):
        """Simple get."""
        url = reverse('group list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Simple get."""
        url = reverse('group', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """
        Test to get group form.
        Simulate it in POST method.
        Test to get new group.
        """
        # Test to get form
        url = reverse('group add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to add
        POST = { 'name': 'new test' }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get
        url = reverse('group', args=[3])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """
        Simulate a POST which change a group.
        Test to see if group's name changed.
        """
        # Test to update
        url = reverse('group update', args=[1])
        POST = { 'name': 'new test' }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test if updated
        group = Group.objects.get(pk=1)
        self.assertEqual(group.name, 'new test', 'Username is not changed (%s).' % group.name)

    def test_delete(self):
        """
        Test to delete group and if can't get it.
        """
        # Test to delete
        url = reverse('group delete', args=[1])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get it
        url = reverse('group', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)


class Configuration_Storage_TestCase(TestCase):
    fixtures = ['test_users.json','test_storage.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def tearDown(self):
        Storage.objects.all().delete()

    def test_index(self):
        """Simple get."""
        url = reverse('storage index')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    ## TODO : enable when done
    # def test_list(self):
    #     """Simple get."""
    #     url = reverse('storage list')
    #     r = self.c.get(url)
    #     self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Simple get."""
        url = reverse('storage', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """
        Test to get storage form.
        Simulate it in POST method.
        Test to get new storage.
        """
        # Test to get form
        url = reverse('storage add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to add
        POST = { 'name': 'new test', 'protocol': 'http', 'address': 'localhot' }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get
        url = reverse('storage', args=[2])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """
        Simulate a POST which change a storage.
        Test to see if storage's name changed.
        """
        # Test to update
        url = reverse('storage update', args=[1])
        POST = { 'name': 'new test', 'protocol': 'http', 'address': 'localhot' }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test if updated
        storage = Storage.objects.get(pk=1)
        self.assertEqual(storage.name, 'new test', 'Username is not changed (%s).' % storage.name)

    def test_delete(self):
        """
        Test to delete user and if can't get it.
        """
        # Test to delete
        url = reverse('storage delete', args=[1])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get it
        url = reverse('storage', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)
