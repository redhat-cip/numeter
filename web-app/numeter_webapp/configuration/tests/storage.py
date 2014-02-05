from django.test import LiveServerTestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.models import Storage
from core.tests.utils import set_users, set_clients, set_storage


class Storage_Test(LiveServerTestCase):
    @set_users()
    @set_clients()
    @set_storage()
    def setUp(self):
        pass

    def test_get(self):
        """Get a filled Storage form."""
        url = reverse('storage', args=[self.storage.id])
        r = self.admin_client.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """Get an empty Storage form."""
        url = reverse('storage add')
        r = self.admin_client.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_repair_hosts(self):
        """Repair hosts which have broken links to storages."""
        # Get
        url = reverse('storage bad hosts')
        r = self.admin_client.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Post
        r = self.admin_client.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_create_hosts(self):
        """Create hosts from web interface."""
        url = reverse('storage create hosts', args=[self.storage.id])
        r = self.admin_client.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

