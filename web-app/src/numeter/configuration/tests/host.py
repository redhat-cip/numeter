from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.models import Host
from core.tests.utils import storage_enabled, set_storage


class Host_TestCase(TestCase):
    fixtures = ['test_users.json','test_storage.json']

    @set_storage()
    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')
        self.storage._update_hosts()
        if not Host.objects.exists():
            self.skipTest("There's no host in storage.")

    def tearDown(self):
        Host.objects.all().delete()

    def test_get(self):
        """Get an host."""
        url = reverse('host', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """
        Simulate a POST which change a storage.
        Test to see if host's name changed.
        """
        # Test to update
        url = reverse('host update', args=[1])
        POST = { 'name': 'test host', 'storage': 1, 'hostid': 'test id' }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test if updated
        host = Host.objects.get(pk=1)
        self.assertEqual(host.name, 'test host', 'Username is not changed (%s).' % host.name)

    def test_delete(self):
        """Test to delete user and if can't get it. """
        # Test to delete
        url = reverse('host delete', args=[1])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get it
        url = reverse('host', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)

    def test_show_plugins(self):
        """Show a table of plugins."""
        url = reverse('host plugins', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
