from django.test import TestCase
from core.models import Storage, Host
from core.tests.utils import storage_enabled, set_storage


class Host_TestCase(TestCase):
    fixtures = ['test_storage.json']

    @set_storage()
    def setUp(self):
        self.storage._update_hosts()
        if not Host.objects.exists():
            self.skipTest("There's no host in storage.")
        self.host = Host.objects.all()[0]

    def tearDown(self):
        Host.objects.all().delete()

    @storage_enabled()
    def test_get_info(self):
        """Retrieve info."""
        r = self.host.get_info()
        self.assertIsInstance(r, dict, "Invalide response type, should be dict.")

    @storage_enabled()
    def test_get_categories(self):
        """Retrieve plugins categories."""
        r = self.host.get_categories()
        self.assertIsInstance(r, list, "Invalide response type, should be list.")

    @storage_enabled()
    def test_get_plugins(self):
        """Retrieve all plugins."""
        r = self.host.get_plugins()
        # self.assertIsInstance(r, list, "Invalide response type, should be list.")

    @storage_enabled()
    def test_get_plugins_by_category(self):
        """Retrieve plugins only for a category."""
        category = self.host.get_categories()[0]
        r = self.host.get_plugins_by_category(category)
        self.assertIsInstance(r, list, "Invalide response type, should be list.")

    @storage_enabled()
    def test_get_plugins_data_sources(self):
        """Retrieve data sources a plugin."""
        plugin = self.host.get_plugins()[0]['Plugin']
        r = self.host.get_plugin_data_sources(plugin)
        self.assertIsInstance(r, list, "Invalide response type, should be list.")

    @storage_enabled()
    def test_get_data(self):
        """Retrieve data sources a plugin."""
        plugin = self.host.get_plugins()[0]['Plugin']
        source = self.host.get_plugin_data_sources(plugin)[0]
        data = {'plugin':plugin, 'ds':source, 'res':'Daily'}
        r = self.host.get_data(**data)
        self.assertIsInstance(r, dict, "Invalide response type, should be dict.")
