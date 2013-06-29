from django.test import TestCase
from django.test.client import Client


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

    def test_index(self):
        url = '/configuration'
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
