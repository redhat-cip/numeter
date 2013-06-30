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
        self.u = User.objects.get(pk=1)

    def test_index(self):
        url = '/configuration'
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_change_username(self):
        url = self.u.get_update_url()
        r = self.c.post(url, {'username':'toto'})
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        self.assertTrue(User.objects.filter(username='toto').exists(), "New username not foundable.")

    def test_change_password(self):
        url = self.u.get_update_password_url()
        POST = {'old':'toto','new_1':'root','new_2':'root'}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        self.c.logout()
        is_logged = self.c.login(username='root', password='toto')
        self.assertFalse(is_logged, 'User can log with old credentials.')

        is_logged = self.c.login(username='root', password='root')
        self.assertTrue(is_logged, "User can't log with new credentials.")
