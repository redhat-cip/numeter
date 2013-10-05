from django.test import LiveServerTestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core import management

from core.models import Host, Plugin, Data_Source
from core.tests.utils import storage_enabled, set_storage
from multiviews.models import View
from multiviews.tests.utils import create_view


class Customize_View_Test(LiveServerTestCase):
    fixtures = ['test_users.json']

    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')
        self.host = Host.objects.all()[0]
        self.plugin = Plugin.objects.all()[0]
        self.source = Data_Source.objects.all()[0]

    def tearDown(self):
        Plugin.objects.all().delete()
        Data_Source.objects.all().delete()

    def test_index(self):
        """Get view index."""
        url = reverse('multiviews customize view index')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_list(self):
        """Get view list."""
        url = reverse('multiviews customize view list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """Get adding view."""
        # Test GET
        url = reverse('multiviews customize view add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a source."""
        self.view = create_view()
        url = reverse('multiviews customize view edit', args=[self.view.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
