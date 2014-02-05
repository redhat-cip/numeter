from django.test import LiveServerTestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.models import Host, Plugin, Data_Source
from core.tests.utils import set_users, set_clients, set_storage
from multiviews.models import View, Multiview
from multiviews.tests.utils import create_view, create_multiview


class Multiview_Test(LiveServerTestCase):
    @set_users()
    @set_clients()
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        self.view = create_view()
        self.multiview = create_multiview()

    def test_add(self):
        url = reverse('multiview add')
        r = self.admin_client.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a multiview."""
        multiview = Multiview.objects.create(name='test multiview')
        url = reverse('multiview', args=[multiview.id])
        r = self.admin_client.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """
        Simulate a POST which change a multiview.
        Test to see if comment has changed.
        """
        multiview = Multiview.objects.create(name='test multiview')
        # Test to update
        url = reverse('multiview update', args=[multiview.id])
        POST = {'name':'test multiview'}
        r = self.admin_client.post(url, POST) 
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test if updated
        multiview = Multiview.objects.get(pk=multiview.pk)
        self.assertEqual(multiview.name, 'test multiview', 'Comment is not changed (%s).' % multiview.name)
