"""
Source model tests module.
"""

from django.test import LiveServerTestCase
from core.models import Storage, Host, Plugin, Group, Data_Source as Source
from core.tests.utils import False_HttpRequest_dict, set_storage, set_users


class Source_Manager_user_filter_Test(LiveServerTestCase):
    """
    Test filter source by his user attribute.
    """
    @set_storage(extras=['host','plugin','source'])
    @set_users()
    def setUp(self):
        pass

    def test_grant_to_super_user(self):
        """Superuser access to every sources."""
        sources = Source.objects.user_filter(self.admin)
        self.assertEqual(sources.count(), Source.objects.count(), "Superuser can't access to all sources")

    def test_grant_super_simple_with_his_source(self):
        """User access to his group sources."""
        sources = Source.objects.user_filter(self.user)
        manual_filtered = Source.objects.filter(plugin__host=self.host)
        self.assertEqual(sources.count(), manual_filtered.count(), "User can't access to his sources.")

    def test_forbid_to_simple_user_with_not_owned_plugin(self):
        """User doesn't access to a not owned source."""
        sources = Source.objects.user_filter(self.user2)
        self.assertEqual(sources.count(), 0, "User can access to a not owned source.")

    def test_forbid_to_simple_user_with_foreign_source(self):
        """User doesn't access to a source owned by other user."""
        new_group = Group.objects.create(name='NEW GROUP')
        self.host.group = new_group
        self.host.save()
        sources = Source.objects.user_filter(self.user2)
        self.assertEqual(sources.count(), 0, "User can access to a source owned by other group.")


class Source_Manager_Test(LiveServerTestCase):

    @set_storage(extras=['host','plugin'])
    def setUp(self):
        self.host = Host.objects.all()[0]

    def tearDown(self):
        Host.objects.all().delete()

    def test_full_create(self):
        """Test ``Data_Source.objects.full_create``."""
        available_sources = []
        for plugin in Plugin.objects.all():
            available_sources = plugin.get_data_sources()
            if len(available_sources) >= 2: break
        # Create one
        POST = False_HttpRequest_dict({
          'host': plugin.host.hostid,
          'plugin': plugin.name,
          'sources[]': available_sources[:1]
        })
        Plugin.objects.all().delete()
        sources = Source.objects.full_create(POST)
        self.assertEqual(len(sources), 1,
            "Bad number of created sources (%i), should be 1." % len(sources)
        )
        # Create the same
        sources = Source.objects.full_create(POST)
        self.assertEqual(len(sources), 0,
            "Bad number of created sources (%i), should be 0." % len(sources)
        )
        # Create source and plugin
        POST['plugin'] = plugin.name
        plugin.delete()
        Source.objects.all().delete()
        sources = Source.objects.full_create(POST)
        self.assertEqual(len(sources), 1,
            "Bad number of created sources (%i), should be 1." % len(sources)
        )
        plugin_count = Plugin.objects.filter(name=POST['plugin']).count()
        self.assertEqual(plugin_count, 1,
            "Bad number of created plugin (%i), should be 1." % plugin_count
        )
        # Create with false source
        POST['sources[]'] = ['test']
        sources = Source.objects.full_create(POST)
        self.assertEqual(len(sources), 0,
            "Bad number of created sources (%i), should be 0." % len(sources)
        )
        # Create with false plugin
        POST['plugin'] = 'test'
        try: Source.objects.full_create(POST)
        except ValueError: pass
        else: assert("Can store false plugin in db.")


class Source_Test(LiveServerTestCase):

    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        self.host = Host.objects.all()[0]
        self.plugin = Plugin.objects.all()[0]
        self.source = Source.objects.all()[0]

    def test_get_data(self):
        """Retrieve data."""
        data = {'res':'Daily'}
        r = self.source.get_data(**data)
        self.assertIsInstance(r, dict, "Invalide response type, should be dict.")
