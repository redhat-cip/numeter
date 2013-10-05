from django.test import LiveServerTestCase
from core.models import Storage, Host, Plugin, Data_Source
from core.tests.utils import False_HttpRequest_dict, storage_enabled, set_storage


class Source_Manager_Test(LiveServerTestCase):

    @set_storage(extras=['host','plugin'])
    def setUp(self):
        self.host = Host.objects.all()[0]
        self.plugin = Plugin.objects.all()[0]

    def tearDown(self):
        Host.objects.all().delete()

    def test_full_create(self):
        available_sources = self.plugin.get_data_sources()
        # Create one
        POST = False_HttpRequest_dict({
          'host': self.host.hostid,
          'plugin': self.plugin.name,
          'sources[]': available_sources[:1]
        })
        sources = Data_Source.objects.full_create(POST)
        self.assertEqual(len(sources), 1,
            "Bad number of created sources (%i), should be 1." % len(sources)
        )
        # Create the same
        sources = Data_Source.objects.full_create(POST)
        self.assertEqual(len(sources), 0,
            "Bad number of created sources (%i), should be 0." % len(sources)
        )
        # Create source and plugin
        POST['plugin'] = self.plugin.name
        self.plugin.delete()
        Data_Source.objects.all().delete()
        sources = Data_Source.objects.full_create(POST)
        self.assertEqual(len(sources), 1,
            "Bad number of created sources (%i), should be 1." % len(sources)
        )
        plugin_count = Plugin.objects.filter(name=POST['plugin']).count()
        self.assertEqual(plugin_count, 1,
            "Bad number of created sources (%i), should be 1." % plugin_count
        )
        # Create with false source
        POST['sources[]'] = ['test']
        sources = Data_Source.objects.full_create(POST)
        self.assertEqual(len(sources), 0,
            "Bad number of created sources (%i), should be 0." % len(sources)
        )
        # Create with false plugin
        POST['plugin'] = 'test'
        try: Data_Source.objects.full_create(POST)
        except ValueError: pass
        else: assert("Can store false plugin in db.")


class Source_Test(LiveServerTestCase):

    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        self.host = Host.objects.all()[0]
        self.plugin = Plugin.objects.all()[0]
        self.source = Data_Source.objects.all()[0]

    @storage_enabled()
    def test_get_data(self):
        """Retrieve data."""
        data = {'res':'Daily'}
        r = self.source.get_data(**data)
        self.assertIsInstance(r, dict, "Invalide response type, should be dict.")
