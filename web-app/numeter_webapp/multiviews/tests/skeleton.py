from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from core.models import Host, Plugin, Data_Source as Source
from core.tests.utils import storage_enabled, set_storage
from multiviews.models import View, Skeleton
from multiviews.tests.utils import create_view, create_event


class Skeleton_Test(LiveServerTestCase):

    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        self.source = Source.objects.all()[0]
        self.skeleton = Skeleton.objects.create(
            name="TEST",
            plugin_pattern=self.source.plugin.name,
            source_pattern=self.source.name
        )

    def test_create_view(self):
        """Create view from skeleton."""
        hosts = Host.objects.all()
        view = self.skeleton.create_view('TEST', hosts)
        self.assertTrue(View.objects.exists(), "No new view.")

    def test_create_view_without_existing(self):
        """Create a view and its plugins and sources."""
        [ p.delete() for p in Plugin.objects.all() ]
        hosts = Host.objects.all()
        view = self.skeleton.create_view('TEST', hosts)
        self.assertTrue(Plugin.objects.exists(), "No automatic plugin creation.")
        self.assertTrue(Source.objects.exists(), "No automatic source creation.")
        self.assertTrue(View.objects.exists(), "No new view.")
