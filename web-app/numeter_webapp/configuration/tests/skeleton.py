from django.test import LiveServerTestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from core.tests.utils import set_users
from multiviews.models import View, Skeleton


class Skeleton_Test(LiveServerTestCase):
    @set_users()
    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def test_list(self):
        """Get skeleton list."""
        url = reverse('skeleton list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """
        Test to get skeleton form.
        Simulate it in POST method.
        Test to get new skeleton.
        """
        # Test to get form
        url = reverse('skeleton add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test to add
        POST = {'name': 'test skeleton', 'plugin_pattern':'.', 'source_pattern':'.'}
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        skeleton = Skeleton.objects.get(name='test skeleton')
        # Test to get
        skeleton = Skeleton.objects.get(pk=skeleton.pk)
        url = reverse('skeleton', args=[skeleton.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a skeleton."""
        skeleton = Skeleton.objects.create(name='test skeleton', plugin_pattern='.', source_pattern='.')
        url = reverse('skeleton', args=[skeleton.id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """
        Simulate a POST which change a skeleton.
        Test to see if comment has changed.
        """
        skeleton = Skeleton.objects.create(name='test skeleton', plugin_pattern='.', source_pattern='.')
        # Test to update
        url = reverse('skeleton update', args=[skeleton.id])
        POST = skeleton.__dict__
        POST.update({'name':'test skeleton'})
        r = self.c.post(url, POST) 
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test if updated
        skeleton = Skeleton.objects.get(pk=skeleton.pk)
        self.assertEqual(skeleton.name, 'test skeleton', 'Name is not changed (%s).' % skeleton.name)

    def test_delete(self):
        """Test to delete skeleton and if can't get it."""
        skeleton = Skeleton.objects.create(name='test skeleton', plugin_pattern='.', source_pattern='.')
        skeleton_id = skeleton.id
        # Test to delete
        url = reverse('skeleton delete', args=[skeleton_id])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

        # Test to get it
        url = reverse('skeleton', args=[skeleton_id])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)

