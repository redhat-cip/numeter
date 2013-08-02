from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core import management
from django.conf import settings

from core.models import User, Storage, Host
from multiviews.models import Plugin, Data_Source, View, Multiview


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
        Host.objects.all().delete()
        Plugin.objects.all().delete()
        Data_Source.objects.all().delete()

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
        # Test GET
        url = reverse('plugin create')
        GET = {'host_id':self.host.id}
        r = self.c.get(url, GET)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        plugins = [ p['Plugin'] for p in self.host.get_plugins() ]
        chosen_plugins = plugins[:1]
        POST = {'host_id':self.host.id, 'plugins[]':chosen_plugins}
        r = self.c.post(url, POST)
        # Test if plugins have been created
        saved_plugins = Plugin.objects.all()
        self.assertTrue(saved_plugins.exists(), "No plugin have been created.")

        # Test to create false plugin
        POST = {'host_id':self.host.id, 'plugins[]':['FALSE']}
        r = self.c.post(url, POST)
        saved_plugins = Plugin.objects.all()
        self.assertEqual(saved_plugins.count(), 1, "False plugins can be created.")

        # Test to recreate a plugin
        POST = {'host_id':self.host.id, 'plugins[]':chosen_plugins}
        r = self.c.post(url, POST)
        saved_plugins = Plugin.objects.all()
        self.assertEqual(saved_plugins.count(), 1, "Can create duplicate plugin.")

    def test_get(self):
        """Get a plugin."""
        plugin = Plugin.objects.create_from_host(self.host)[0]
        url = reverse('plugin', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_create_sources(self):
        """Create sources from a plugin."""
        plugin = Plugin.objects.create_from_host(self.host)[0]
        # Test GET
        url = reverse('plugin create sources', args=[plugin.id])
        GET = {'host_id':self.host.id}
        r = self.c.get(url, GET)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        sources = plugin.get_data_sources()
        chosen_sources = sources[:1]
        POST = {'host_id':self.host.id, 'sources[]':chosen_sources}
        r = self.c.post(url, POST)
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
        plugin = Plugin.objects.create_from_host(self.host)[0]
        # Test to delete
        url = reverse('plugin delete', args=[plugin.id])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get it
        url = reverse('plugin', args=[plugin.id])
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
        View.objects.all().delete()

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


class Configuration_View_TestCase(TestCase):
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

    def tearDown(self):
        Plugin.objects.all().delete()
        Data_Source.objects.all().delete()
        View.objects.all().delete()

    def test_source_list(self):
        """Get view list."""
        url = reverse('view list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """
        Test to get view form.
        Simulate it in POST method.
        Test to get new view.
        """
        # Test to get form
        url = reverse('view add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to add
        POST = { 'name': 'test view', 'sources': [1]}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get
        view = View.objects.get(name='test view')
        url = reverse('view', args=[view.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a view."""
        view = View.objects.create(name='test view')
        url = reverse('view', args=[view.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """
        Simulate a POST which change a view.
        Test to see if comment has changed.
        """
        view = View.objects.create(name='test view')
        # Test to update
        url = reverse('source update', args=[view.id])
        POST = {'name':'test view'}
        r = self.c.post(url, POST) 
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test if updated
        view = View.objects.get(pk=view.pk)
        self.assertEqual(view.name, 'test view', 'Comment is not changed (%s).' % view.name)

    def test_delete(self):
        """Test to delete view and if can't get it."""
        view = View.objects.create(name='test view')
        view_id = view.id
        # Test to delete
        url = reverse('view delete', args=[view_id])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get it
        url = reverse('view', args=[view_id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)


class Configuration_Multiview_TestCase(TestCase):
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
        self.view = View.objects.create(name='test view')

    def tearDown(self):
        Plugin.objects.all().delete()
        Data_Source.objects.all().delete()
        Multiview.objects.all().delete()
        Multiview.objects.all().delete()

    def test_list(self):
        """Get multiview list."""
        url = reverse('multiview list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """
        Test to get multiview form.
        Simulate it in POST method.
        Test to get new multiview.
        """
        # Test to get form
        url = reverse('multiview add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to add
        POST = {'name': 'test multiview', 'views': [str(self.view.id)]}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        multiview = Multiview.objects.get(name='test multiview')

        # Test to get
        multiview = Multiview.objects.get(pk=multiview.pk)
        url = reverse('multiview', args=[multiview.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a multiview."""
        multiview = Multiview.objects.create(name='test multiview')
        url = reverse('multiview', args=[multiview.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """
        Simulate a POST which change a multiview.
        Test to see if comment has changed.
        """
        multiview = Multiview.objects.create(name='test multiview')
        # Test to update
        url = reverse('source update', args=[multiview.id])
        POST = {'name':'test multiview'}
        r = self.c.post(url, POST) 
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test if updated
        multiview = Multiview.objects.get(pk=multiview.pk)
        self.assertEqual(multiview.name, 'test multiview', 'Comment is not changed (%s).' % multiview.name)

    def test_delete(self):
        """Test to delete multiview and if can't get it."""
        multiview = Multiview.objects.create(name='test multiview')
        multiview_id = multiview.id
        # Test to delete
        url = reverse('multiview delete', args=[multiview_id])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get it
        url = reverse('multiview', args=[multiview_id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)
