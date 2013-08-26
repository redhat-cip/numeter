from django.test import TestCase
from core.models import Storage, Host, Plugin, Data_Source
from core.tests.utils import storage_enabled, set_storage


class Data_Source_TestCase(TestCase):
    fixtures = ['test_storage.json']

    @set_storage()
    def setUp(self):
        self.storage._update_hosts()
        if not Host.objects.exists():
            self.skipTest("There's no host in storage.")
        self.host = Host.objects.all()[0]
        self.plugin = self.host.create_plugins()[0]
        self.source = self.plugin.create_data_sources()[0]

    def tearDown(self):
        Host.objects.all().delete()

    @storage_enabled()
    def test_get_data(self):
        """Retrieve data."""
        data = {'res':'Daily'}
        r = self.source.get_data(**data)
        self.assertIsInstance(r, dict, "Invalide response type, should be dict.")
