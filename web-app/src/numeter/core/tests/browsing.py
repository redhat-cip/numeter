from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from core.models import User, Storage


class Index_TestCase(TestCase):
    fixtures = ['test_users.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def test_index(self):
        url = '/'
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_apropos(self):
        url = '/apropos'
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)


class Multiviews_TestCase(TestCase):
    fixtures = ['test_users.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def test_index(self):
        url = '/multiviews'
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
        url = '/configuration'
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_change_username(self):
        url = self.admin.get_update_url()
        r = self.c.post(url, {'username': 'toto', 'graph_lib': 1})
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        self.assertTrue(User.objects.filter(username='toto').exists(), "New username not foundable.")

    def test_change_own_password(self):
        self.c.logout()
        self.c.login(username='test', password='toto')

        url = self.user.get_update_password_url()
        POST = {'old':'toto','new_1':'root','new_2':'root'}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        self.user = User.objects.get(pk=2)
        self.assertTrue(self.user.check_password('root'), "Password doesn't change.")

    def test_admin_change_password(self):
        url = self.user.get_update_password_url()
        POST = {'old':'toto','new_1':'root','new_2':'root'}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        self.user = User.objects.get(pk=2)
        self.assertTrue(self.user.check_password('root'), "New password checking failed.")

    def test_forbidden_change_password(self):
        self.c.logout()
        self.c.login(username='test', password='toto')

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
        url = reverse('user index')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_list(self):
        url = reverse('user list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_superuser_list(self):
        url = reverse('superuser list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        url = reverse('user', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        url = reverse('user add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        POST = { 'username': 'new test', 'graph_lib': 1 }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        url = reverse('user', args=[3])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        url = reverse('user update', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        POST = { 'username': 'new test', 'graph_lib': 1 }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        user = User.objects.get(pk=1)
        self.assertEqual(user.username, 'new test', 'Username is not changed (%s).' % user.username)

    def test_delete(self):
        url = reverse('user delete', args=[2])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

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
        url = reverse('group list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        url = reverse('group', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        url = reverse('group add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        POST = { 'name': 'new test' }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        url = reverse('group', args=[3])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        url = reverse('group update', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        POST = { 'name': 'new test' }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        group = Group.objects.get(pk=1)
        self.assertEqual(group.name, 'new test', 'Username is not changed (%s).' % group.name)

    def test_delete(self):
        url = reverse('group delete', args=[1])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

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
        url = reverse('storage index')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    ## TODO : enable when done
    # def test_list(self):
    #     url = reverse('storage list')
    #     r = self.c.get(url)
    #     self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        url = reverse('storage', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        url = reverse('storage add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        POST = { 'name': 'new test', 'protocol': 'http', 'address': 'localhot' }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        url = reverse('storage', args=[2])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        url = reverse('storage update', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        POST = { 'name': 'new test', 'protocol': 'http', 'address': 'localhot' }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        storage = Storage.objects.get(pk=1)
        self.assertEqual(storage.name, 'new test', 'Username is not changed (%s).' % storage.name)

    def test_delete(self):
        url = reverse('storage delete', args=[1])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        url = reverse('storage', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)
