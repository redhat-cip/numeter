"""
Host model tests module.
"""

from django.test import LiveServerTestCase
from core.models import Host, Plugin, Group
from core.tests.utils import set_storage, set_users


class Host_Manager_user_filter_Test(LiveServerTestCase):
    """
    Test filter host by his user attribute.
    """
    @set_storage(extras=['host'])
    @set_users()
    def setUp(self):
        pass

    def test_grant_to_super_user(self):
        """Superuser access to every hosts."""
        hosts = Host.objects.user_filter(self.admin)
        self.assertEqual(hosts.count(), Host.objects.count(), "Superuser can't access to all hosts")

    def test_grant_super_simple_with_his_host(self):
        """User access to his group host."""
        hosts = Host.objects.user_filter(self.user)
        self.assertEqual(hosts.count(), 1, "User can't access to his host")

    def test_forbid_to_simple_user_with_not_owned_host(self):
        """User doesn't access to a not owned host."""
        hosts = Host.objects.user_filter(self.user2)
        self.assertEqual(hosts.count(), 0, "User can access to a not owned host.")

    def test_forbid_to_simple_user_with_foreign_host(self):
        """User doesn't access to a host owned by other group."""
        new_group = Group.objects.create(name='NEW GROUP')
        self.host.group = new_group
        self.host.save()
        hosts = Host.objects.user_filter(self.user2)
        self.assertEqual(hosts.count(), 0, "User can access to a user owned by other group.")


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
