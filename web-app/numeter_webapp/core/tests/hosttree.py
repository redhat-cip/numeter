from django.test import LiveServerTestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.models import User, Storage, Host
from core.tests.utils import storage_enabled, set_storage


class Hosttree_Test(LiveServerTestCase):
    """Test hosttree views."""
    fixtures = ['test_users.json','test_groups.json']

    @set_storage(extras=['host'])
    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    @storage_enabled()
    def test_group(self):
        """Get hosts from group."""
        url = reverse('hosttree group', args=[''])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    @storage_enabled()
    def test_host(self):
        """Get plugin's categories from host."""
        url = reverse('hosttree host', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    @storage_enabled()
    def test_category(self):
        """Get plugins from category."""
        H = Host.objects.get(pk=1)
        category = H.get_categories()[0]

        url = reverse('hosttree category', args=[1])
        GET = {'category':category}
        r = self.c.get(url, GET)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
