from django.test import LiveServerTestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.models import Host
from core.tests.utils import set_users, set_clients, set_storage


class Host_Test(LiveServerTestCase):
    @set_storage(extras=['host'])
    @set_users()
    @set_clients()
    def setUp(self):
        pass

    def test_get(self):
        """Get a filled Host form."""
        url = reverse('host', args=[self.host.id])
        r = self.admin_client.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_show_plugins(self):
        """Show a table of plugins."""
        url = reverse('host plugins', args=[self.host.id])
        r = self.admin_client.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
