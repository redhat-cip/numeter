from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from core.models import Storage


class Storage_TestCase(TestCase):
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
        """Test to delete user and if can't get it. """
        # Test to delete
        url = reverse('storage delete', args=[1])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test to get it
        url = reverse('storage', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)

    def test_repair_hosts(self):
        """Repair hosts which have broken links to storages."""
        # Get
        url = reverse('storage bad hosts')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Post
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_create_hosts(self):
        """Create hosts from web interface."""
        url = reverse('storage create hosts', args=[1])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

