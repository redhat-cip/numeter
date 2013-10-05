from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from core.models import Host, Plugin, Data_Source
from core.tests.utils import storage_enabled, set_storage
from multiviews.models import View, Event
from multiviews.tests.utils import create_view, create_event


class View_Test(LiveServerTestCase):
    fixtures = ['test_users.json']

    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        self.host = Host.objects.all()[0]
        self.plugin = Plugin.objects.all()[0]
        self.source = Data_Source.objects.all()[0]
        self.view = create_view()

    def tearDown(self):
        Plugin.objects.all().delete()
        Data_Source.objects.all().delete()
        View.objects.all().delete()
        Event.objects.all().delete()

    def test_get_events(self):
        """Get event(s) for a view.""" 
        event = create_event()
        events = self.view.get_events()
        self.assertTrue(events, "Empty result.")

    def test_get_data(self):
        """Retrieve data."""
        data = {'res':'Daily'}
        r = self.view.get_data(**data)
        self.assertIsInstance(r, list, "Invalide response type, should be list.")

    def test_get_extended_data(self):
        """Retrieve extended data."""
        data = {'res':'Daily'}
        r = self.view.get_data(**data)
        self.assertIsInstance(r, list, "Invalide response type, should be dict.")
