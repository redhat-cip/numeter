from django.test import LiveServerTestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.tests.utils import set_users, set_storage
from multiviews.models import View


class View_Test(LiveServerTestCase):
    @set_users()
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def test_source_list(self):
        """Get view list."""
        url = reverse('view list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """
        Test to get view form.
        Simulate it in POST method.
        Test to get new view.
        """
        # Test to get form
        url = reverse('view add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test to add
        POST = { 'name': 'test view', 'sources': [1]}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test to get
        view = View.objects.get(name='test view')
        url = reverse('view', args=[view.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a view."""
        view = View.objects.create(name='test view')
        url = reverse('view', args=[view.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """
        Simulate a POST which change a view.
        Test to see if comment has changed.
        """
        view = View.objects.create(name='test view')
        # Test to update
        url = reverse('source update', args=[view.id])
        POST = {'name':'test view'}
        r = self.c.post(url, POST) 
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test if updated
        view = View.objects.get(pk=view.pk)
        self.assertEqual(view.name, 'test view', 'Comment is not changed (%s).' % view.name)

    def test_delete(self):
        """Test to delete view and if can't get it."""
        view = View.objects.create(name='test view')
        view_id = view.id
        # Test to delete
        url = reverse('view delete', args=[view_id])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test to get it
        url = reverse('view', args=[view_id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)
