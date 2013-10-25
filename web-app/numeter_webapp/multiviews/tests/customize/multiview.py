from django.test import LiveServerTestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core import management

from core.models import Host, Plugin, Data_Source
from core.tests.utils import storage_enabled, set_storage
from multiviews.models import View, Multiview
from multiviews.tests.utils import create_multiview


class Customize_Multiview_Test(LiveServerTestCase):
    fixtures = ['test_users.json']

    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')
        self.host = Host.objects.all()[0]
        self.plugin = Plugin.objects.all()[0]
        self.source = Data_Source.objects.all()[0]

    def test_index(self):
        """Get multiview index."""
        url = reverse('multiviews customize multiview index')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_list(self):
        """Get multiview list."""
        url = reverse('multiviews customize multiview list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """Get adding multiview."""
        url = reverse('multiviews customize multiview add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a multiview."""
        self.multiview = create_multiview()
        url = reverse('multiviews customize multiview edit', args=[self.multiview.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """Get updating multiview."""
        self.multiview = create_multiview()
        url = reverse('multiviews customize multiview edit', args=[self.multiview.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
