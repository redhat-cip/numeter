from django.test import TestCase
from django.test.client import Client


class Index_TestCase(TestCase):
    fixtures = ['test_users.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def test_index(self):
        url = '/'
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200, "Can't get url %s." % url)


class Multiviews_TestCase(TestCase):
    fixtures = ['test_users.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def test_index(self):
        url = '/multiviews'
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200, "Can't get url %s." % url)


class Configuration_TestCase(TestCase):
    fixtures = ['test_users.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def test_index(self):
        url = '/configuration'
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200, "Can't get url %s." % url)
