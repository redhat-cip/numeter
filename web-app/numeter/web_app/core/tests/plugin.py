from django.test import TestCase
from django.core import management
from django.conf import settings

from core.models import Storage, Host, Plugin, Data_Source
from core.tests.utils import storage_enabled, set_storage


class Plugin_Manager_TestCase(TestCase):

    @set_storage()
    def setUp(self):
        self.storage._update_hosts()
        if not Host.objects.exists():
            self.skipTest("There's no host in storage.")
        self.host = Host.objects.all()[0]

    def tearDown(self):
        Host.objects.all().delete()


class Plugin_TestCase(TestCase):

    @set_storage(extras=['host','plugin'])
    def setUp(self):
        self.host = Host.objects.all()[0]
        self.plugin = Plugin.objects.all()[0]

    def tearDown(self):
        Host.objects.all().delete()
        Plugin.objects.all().delete()
        Data_Source.objects.all().delete()

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
        new_sources = self.plugin.create_data_sources(sources[:1])
        self.assertFalse(new_sources, "Data source created twice times.")

    @storage_enabled()
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
        new = self.plugin.create_data_sources(sources[:1])
        unsaved = self.plugin.get_unsaved_sources()
        self.assertEqual(len(sources)-1, len(unsaved), 
          ("False result (%i), length should be %i." % (len(unsaved), len(sources))) 
        )
