from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from core.models import Host
from core.tests.utils import storage_enabled, set_storage
from multiviews.models import Event
from multiviews.tests.utils import create_event


class Event_Test(LiveServerTestCase):

    @set_storage(extras=['host'])
    def setUp(self):
        self.host = Host.objects.all()[0]

    def tearDown(self):
        Event.objects.all().delete()
