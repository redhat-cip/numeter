from django.test import LiveServerTestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.models import Host, Plugin, Data_Source
from core.tests.utils import storage_enabled, set_storage
from multiviews.models import View, Multiview


class Multiview_Test(LiveServerTestCase):
    fixtures = ['test_users.json','test_storage.json']

    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')
        self.view = View.objects.create(name='test view')

    def test_list(self):
        """Get multiview list."""
        url = reverse('multiview list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """
        Test to get multiview form.
        Simulate it in POST method.
        Test to get new multiview.
        """
        # Test to get form
        url = reverse('multiview add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to add
        POST = {'name': 'test multiview', 'views': [str(self.view.id)]}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        multiview = Multiview.objects.get(name='test multiview')

        # Test to get
        multiview = Multiview.objects.get(pk=multiview.pk)
        url = reverse('multiview', args=[multiview.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a multiview."""
        multiview = Multiview.objects.create(name='test multiview')
        url = reverse('multiview', args=[multiview.id])
        r = self.c.get(url)
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
        r = self.c.post(url, POST) 
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test if updated
        multiview = Multiview.objects.get(pk=multiview.pk)
        self.assertEqual(multiview.name, 'test multiview', 'Comment is not changed (%s).' % multiview.name)

    def test_delete(self):
        """Test to delete multiview and if can't get it."""
        multiview = Multiview.objects.create(name='test multiview')
        multiview_id = multiview.id
        # Test to delete
        url = reverse('multiview delete', args=[multiview_id])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get it
        url = reverse('multiview', args=[multiview_id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)

