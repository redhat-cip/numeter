from django.test import LiveServerTestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.models import Host
from core.tests.utils import storage_enabled, set_storage
from multiviews.models import Event


class Event_Test(LiveServerTestCase):
    fixtures = ['test_users.json','test_storage.json']

    @set_storage(extras=['host'])
    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')
        self.host = Host.objects.all()[0]

    def tearDown(self):
        Event.objects.all().delete()

    def test_source_list(self):
        """Get event list."""
        url = reverse('event list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """
        Test to get event form.
        Simulate it in POST method.
        Test to get new event.
        """
        # Test to get form
        url = reverse('event add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to add
        POST = { 'name': 'test event', 'hosts': [1]}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get
        event = Event.objects.get(name='test event')
        url = reverse('event', args=[event.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a event."""
        event = Event.objects.create(name='test event')
        url = reverse('event', args=[event.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """
        Simulate a POST which change a event.
        Test to see if comment has changed.
        """
        event = Event.objects.create(name='test event')
        # Test to update
        url = reverse('event update', args=[event.id])
        POST = {'name':'test event'}
        r = self.c.post(url, POST) 
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test if updated
        event = Event.objects.get(pk=event.pk)
        self.assertEqual(event.name, 'test event', 'Comment is not changed (%s).' % event.name)

    def test_delete(self):
        """Test to delete event and if can't get it."""
        event = Event.objects.create(name='test event')
        event_id = event.id
        # Test to delete
        url = reverse('event delete', args=[event_id])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get it
        url = reverse('event', args=[event_id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)
