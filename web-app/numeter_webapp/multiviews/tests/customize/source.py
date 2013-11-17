from django.test import LiveServerTestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.models import Host, Plugin, Data_Source
from core.tests.utils import storage_enabled, set_storage


class Customize_Source_Test(LiveServerTestCase):
    fixtures = ['test_users.json']

    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')
        self.host = Host.objects.all()[0]
        self.plugin = Plugin.objects.all()[0]
        self.source = Data_Source.objects.all()[0]

    def test_index(self):
        """Get source index."""
        url = reverse('multiviews customize source index')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_list(self):
        """Get source list."""
        url = reverse('multiviews customize source list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a source."""
        url = reverse('multiviews customize source edit', args=[self.source.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """Add one or more source."""
        url = reverse('multiviews customize source add')
        POST = {
          'host': self.host.hostid,
          'plugin': self.plugin.name,
          'sources[]': [ s[0] for s in Data_Source.objects.all().values_list('name') ],
        }
        r = self.c.post(url, data=POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """Update a source."""
        url = reverse('multiviews customize source edit', args=[self.source.id])
        POST = {
          'name': self.source.name,
          'comment': 'Test Comment'
        }
        r = self.c.post(url, data=POST)
        self.source = Data_Source.objects.get(id=self.source.id)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        self.assertEqual(self.source.comment, 'Test Comment', "Comment hasn't changed.")
