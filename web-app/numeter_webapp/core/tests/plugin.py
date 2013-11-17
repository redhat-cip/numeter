"""
PLugin model tests module.
"""

from django.test import LiveServerTestCase
from core.models import Storage, Host, Plugin, Data_Source, Group
from core.tests.utils import set_storage, set_users


class Plugin_Manager_user_filter_Test(LiveServerTestCase):
    """
    Test filter plugin by his user attribute.
    """
    @set_storage(extras=['host','plugin'])
    @set_users()
    def setUp(self):
        pass

    def test_grant_to_super_user(self):
        """Superuser access to every plugins."""
        plugins = Plugin.objects.user_filter(self.admin)
        self.assertEqual(plugins.count(), Plugin.objects.count(), "Superuser can't access to all plugins")

    def test_grant_super_simple_with_his_plugin(self):
        """User access to his group plugin."""
        plugins = Plugin.objects.user_filter(self.user)
        manual_filtered = Plugin.objects.filter(host=self.host)
        self.assertEqual(plugins.count(), manual_filtered.count(), "User can't access to his plugins.")

    def test_forbid_to_simple_user_with_not_owned_plugin(self):
        """User doesn't access to a not owned plugin."""
        plugins = Plugin.objects.user_filter(self.user2)
        self.assertEqual(plugins.count(), 0, "User can access to a not owned plugin.")

    def test_forbid_to_simple_user_with_foreign_plugin(self):
        """User doesn't access to a plugin owned by other user."""
        new_group = Group.objects.create(name='NEW GROUP')
        self.host.group = new_group
        self.host.save()
        plugins = Plugin.objects.user_filter(self.user2)
        self.assertEqual(plugins.count(), 0, "User can access to a user owned by other group.")


class Plugin_Manager_Test(LiveServerTestCase):

    @set_storage()
    def setUp(self):
        pass


class Plugin_Test(LiveServerTestCase):

    @set_storage(extras=['host','plugin'])
    def setUp(self):
        self.host = Host.objects.all()[0]
        self.plugin = Plugin.objects.all()[0]

    def test_get_data_sources(self):
        """Retrieve data sources."""
        r = self.plugin.get_data_sources()
        self.assertIsInstance(r, list, "Invalide response type, should be list.")

    def test_get_data(self):
        """Retrieve data for a source."""
        source = self.plugin.get_data_sources()[0]
        data = {'ds':source, 'res':'Daily'}
        r = self.plugin.get_data(**data)
        self.assertIsInstance(r, dict, "Invalide response type, should be dict.")

    def test_create_data_sources(self):
        """Create sources."""
        sources = self.plugin.get_data_sources()
        # Without args
        new_sources = self.plugin.create_data_sources()
        self.assertTrue(new_sources, "No data source was created.")
        Data_Source.objects.all().delete()
        # Test with args
        new_sources = self.plugin.create_data_sources(sources[:1])
        self.assertTrue(new_sources, "No data source was created.")
        # Test create again
        DEFAULT_COUNT = Data_Source.objects.count()
        self.plugin.create_data_sources(sources[:1])
        self.assertEqual(DEFAULT_COUNT, Data_Source.objects.count(),
                "Data source created twice times.")

    def test_get_unsaved_sources(self):
        """Get sources not saved in db."""
        sources = self.plugin.get_data_sources()
        # Try to find all before creation
        unsaved = self.plugin.create_data_sources()
        self.assertEqual(len(sources), len(unsaved), 
            ("False result (%i), length should be %i." % (len(unsaved), len(sources)) )
        )
        Data_Source.objects.all().delete()
        # Create sources and try to find others
        self.plugin.create_data_sources(sources[:1])
        unsaved = self.plugin.get_unsaved_sources()
        self.assertEqual(len(sources)-1, len(unsaved), 
          ("False result (%i), length should be %i." % (len(unsaved), len(sources))) 
        )
