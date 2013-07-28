from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core import management
from django.conf import settings

from core.models import User, Storage, Host
from multiviews.models import Plugin, Data_Source


class Configuration_Plugin_TestCase(TestCase):
    fixtures = ['test_users.json','test_storage.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')
        if 'mock_storage' in settings.INSTALLED_APPS:
            management.call_command('loaddata', 'mock_storage.json', database='default', verbosity=0)
            self.storage = Storage.objects.get(pk=1)
        elif settings.TEST_STORAGE['address']:
            self.storage = Storage.objects.create(**settings.TEST_STORAGE)
            if not self.storage.is_on():
                self.skipTest("Configured storage unreachable.")
        else:
            self.skipTest("No test storage has been configurated.")

        self.storage._update_hosts()
        if not Host.objects.exists():
            self.skipTest("There's no host in storage.")
        self.host = Host.objects.all()[0]

    def tearDown(self):
        Plugin.objects.all().delete()

    def test_index(self):
        """Get plugin index."""
        url = reverse('plugin index')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_plugin_list(self):
        """Get plugin list."""
        url = reverse('plugin list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_create_plugin_from_host(self):
        """Create plugin from host ids."""
        # Test url
        url = reverse('plugin create')
        POST = {'host_ids':[self.host.id]}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test if plugin have been created
        plugins = Plugin.objects.all()
        self.assertFalse(plugins.exists(), "No plugin have been created.")

    def test_get(self):
        """Get a plugin."""
        plugin = Plugin.objects.create_from_host(self.host)[0]
        url = reverse('plugin', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_create_sources(self):
        """Create sources from a plugin."""
        plugin = Plugin.objects.create_from_host(self.host)[0]
        # Test url
        url = reverse('plugin create sources', args=[plugin.id])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test if sources have been created
        sources = Data_Source.objects.all()
        self.assertTrue(sources.exists(), "No source have been created.")

    def test_update(self):
        """
        Simulate a POST which change a plugin.
        Test to see if comment has changed.
        """
        # Test to update
        plugins = Plugin.objects.create_from_host(self.host)
        plugin = Plugin.objects.get(pk=1)
        url = reverse('plugin update', args=[1])
        POST = { 'comment': 'test comment' }
        r = self.c.post(url, POST) 
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test if updated
        plugin = Plugin.objects.get(pk=1)
        self.assertEqual(plugin.comment, 'test comment', 'Comment is not changed (%s).' % plugin.comment)

    def test_delete(self):
        """
        Test to delete plugin and if can't get it.
        """
        plugins = Plugin.objects.create_from_host(self.host)
        # Test to delete
        url = reverse('plugin delete', args=[1])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get it
        url = reverse('plugin', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)

class Configuration_Source_TestCase(TestCase):
    fixtures = ['test_users.json','test_storage.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')
        if 'mock_storage' in settings.INSTALLED_APPS:
            management.call_command('loaddata', 'mock_storage.json', database='default', verbosity=0)
            self.storage = Storage.objects.get(pk=1)
        elif settings.TEST_STORAGE['address']:
            self.storage = Storage.objects.create(**settings.TEST_STORAGE)
            if not self.storage.is_on():
                self.skipTest("Configured storage unreachable.")
        else:
            self.skipTest("No test storage has been configurated.")

        self.storage._update_hosts()
        if not Host.objects.exists():
            self.skipTest("There's no host in storage.")
        self.host = Host.objects.all()[0]
        plugin = Plugin.objects.create_from_host(self.host)[0]
        plugin.create_data_sources()
        self.source = Data_Source.objects.all()[0]

    def tearDown(self):
        Plugin.objects.all().delete()
        Data_Source.objects.all().delete()

    def test_source_list(self):
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
        POST = { 'comment': 'test comment' }
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
