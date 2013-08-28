from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.models import Host, Plugin, Data_Source
from core.tests.utils import storage_enabled, set_storage


class Source_TestCase(TestCase):
    fixtures = ['test_users.json','test_storage.json']

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

    def test_list(self):
        """Get source list."""
        url = reverse('source list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a source."""
        url = reverse('source', args=[self.source.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """
        Simulate a POST which change a source.
        Test to see if comment has changed.
        """
        # Test to update
        url = reverse('source update', args=[self.source.id])
        POST = { 'name': self.source.name, 'comment': 'test comment' }
        r = self.c.post(url, POST) 
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test if updated
        source = Data_Source.objects.get(pk=self.source.id)
        self.assertEqual(source.comment, 'test comment', 'Comment is not changed (%s).' % source.comment)

    def test_delete(self):
        """
        Test to delete source and if can't get it.
        """
        # Test to delete
        url = reverse('source delete', args=[self.source.id])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test to get it
        url = reverse('source', args=[self.source.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)
