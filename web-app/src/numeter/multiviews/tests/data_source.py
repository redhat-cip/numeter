from django.test import TestCase
from core.models import Storage, Host
from core.tests.utils import storage_enabled, set_storage
from multiviews.models import Plugin, Data_Source


class Data_Source_TestCase(TestCase):
    fixtures = ['test_storage.json']

    @set_storage()
    def setUp(self):
        self.storage._update_hosts()
        if not Host.objects.exists():
            self.skipTest("There's no host in storage.")
        self.host = Host.objects.all()[0]
        self.plugin = Plugin.objects.create_from_host(self.host)[0]
        self.source = self.plugin.create_data_sources()[0]

    def tearDown(self):
        Host.objects.all().delete()

    @storage_enabled()
    def test_get_data(self):
        """Retrieve data."""
        data = {'res':'Daily'}
        r = self.source.get_data(**data)
        self.assertIsInstance(r, dict, "Invalide response type, should be dict.")
