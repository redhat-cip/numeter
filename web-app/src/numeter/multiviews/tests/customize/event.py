from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core import management

from core.models import Host
from core.tests.utils import storage_enabled, set_storage
from multiviews.models import Event
from multiviews.tests.utils import create_event


class Customize_Event_TestCase(TestCase):
    fixtures = ['test_users.json']

    @set_storage(extras=['host'])
    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')
        self.host = Host.objects.all()[0]

    def tearDown(self):
        Event.objects.all().delete()

    def test_index(self):
        """Get event index."""
        url = reverse('multiviews customize event index')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_list(self):
        """Get event list."""
        url = reverse('multiviews customize event list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """Get adding event."""
        url = reverse('multiviews customize event add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a event."""
        self.event = create_event()
        url = reverse('multiviews customize event edit', args=[self.event.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """Get updating event."""
        self.event = create_event()
        url = reverse('multiviews customize event edit', args=[self.event.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
