from django.test import TestCase
from django.test.client import Client
from core.models import User


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


class Configuration_TestCase(TestCase):
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
