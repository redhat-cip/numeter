from django.test import TestCase
from django.core import management
from django.conf import settings

from core.models import Storage, Host
from core.tests.utils import storage_enabled
from multiviews.models import Plugin, Data_Source


class Plugin_Manager_TestCase(TestCase):
    fixtures = ['test_storage.json']

    def setUp(self):
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

    def test_create_host_plugins(self):
        host = Host.objects.all()[0]
        Plugin.objects.create_from_host(host)
        self.assertTrue(Plugin.objects.all().exists(), "No plugin was created.")


class Plugin_TestCase(TestCase):
    fixtures = ['test_storage.json']

    def setUp(self):
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
        self.plugin = Plugin.objects.create_from_host(self.host)[0]

    def tearDown(self):
        Host.objects.all().delete()

    @storage_enabled()
    def test_get_data_sources(self):
        """Retrieve data sources."""
        r = self.plugin.get_data_sources()
        self.assertIsInstance(r, list, "Invalide response type, should be list.")

    @storage_enabled()
    def test_get_data(self):
        """Retrieve data for a source."""
        source = self.plugin.get_data_sources()[0]
        data = {'ds':source, 'res':'Daily'}
        r = self.plugin.get_data(**data)
        self.assertIsInstance(r, dict, "Invalide response type, should be dict.")

    @storage_enabled()
    def test_create_data_sources(self):
        self.plugin.create_data_sources()
        self.assertTrue(Data_Source.objects.all().exists(), "No data source was created.")
