from django.test import LiveServerTestCase
from core.models import Host, Plugin
from core.tests.utils import set_storage


class Host_Test(LiveServerTestCase):

    @set_storage(extras=['host'])
    def setUp(self):
        if not Host.objects.exists():
            self.skipTest("There's no host in storage.")
        self.host = Host.objects.all()[0]

    def test_get_info(self):
        """Retrieve info."""
        r = self.host.get_info()
        self.assertIsInstance(r, dict, "Invalide response type, should be dict.")

    def test_get_categories(self):
        """Retrieve plugins categories."""
        r = self.host.get_categories()
        self.assertIsInstance(r, list, "Invalide response type, should be list.")

    def test_get_plugins(self):
        """Retrieve all plugins."""
        r = self.host.get_plugins()
        # self.assertIsInstance(r, list, "Invalide response type, should be list.")

    def test_get_plugins_by_category(self):
        """Retrieve plugins only for a category."""
        category = self.host.get_categories()[0]
        r = self.host.get_plugins_by_category(category)
        self.assertIsInstance(r, list, "Invalide response type, should be list.")

    def test_get_plugins_data_sources(self):
        """Retrieve data sources a plugin."""
        plugin = self.host.get_plugins()[0]['Plugin']
        r = self.host.get_plugin_data_sources(plugin)
        self.assertIsInstance(r, list, "Invalide response type, should be list.")

    def test_get_data(self):
        """Retrieve data sources a plugin."""
        plugin = self.host.get_plugins()[0]['Plugin']
        source = self.host.get_plugin_data_sources(plugin)[0]
        data = {'plugin':plugin, 'ds':source, 'res':'Daily'}
        r = self.host.get_data(**data)
        self.assertIsInstance(r, dict, "Invalide response type, should be dict.")

    def test_create_plugins(self):
        """Create plugins."""
        plugins = self.host.get_plugin_list()
        # Without args
        new_plugins = self.host.create_plugins()
        self.assertTrue(new_plugins, "No plugin was created.")
        Plugin.objects.all().delete()
        # Test with args
        new_plugins = self.host.create_plugins(plugins[:1])
        self.assertTrue(new_plugins, "No plugin was created.")
        # Test create again
        DEFAULT_COUNT = Plugin.objects.count()
        new_plugins = self.host.create_plugins(plugins[:1])
        self.assertEqual(DEFAULT_COUNT, Plugin.objects.count(),
                "Plugins created twice times.")

    def test_get_unsaved_plugins(self):
        """List plugins aren't in db."""
        plugins = self.host.get_plugin_list()
        # Try to find all before creation
        unsaved = self.host.get_unsaved_plugins()
        self.assertEqual( len(plugins), len(unsaved),
            ("False result (%i), length should be %i." % (len(unsaved), len(plugins)) )
        )
        # Create sources and try to find others
        new = self.host.create_plugins(plugins[:1])
        unsaved = self.host.get_unsaved_plugins()
        self.assertEqual( len(plugins)-1, len(unsaved),
            ("False result (%i), length should be %i." % (len(unsaved), len(plugins)-1) )
        )
