from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from core.models import Group


class Group_TestCase(TestCase):
    fixtures = ['test_users.json', 'test_groups.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def tearDown(self):
        Group.objects.all().delete()

    def test_list(self):
        """Get grup list."""
        url = reverse('group list')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_get(self):
        """Get a group."""
        url = reverse('group', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """
        Test to get group form.
        Simulate it in POST method.
        Test to get new group.
        """
        # Test to get form
        url = reverse('group add')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test to add
        POST = { 'name': 'new test' }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test to get
        url = reverse('group', args=[3])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_update(self):
        """
        Simulate a POST which change a group.
        Test to see if group's name changed.
        """
        # Test to update
        url = reverse('group update', args=[1])
        POST = { 'name': 'new test' }
        r = self.c.post(url, POST)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test if updated
        group = Group.objects.get(pk=1)
        self.assertEqual(group.name, 'new test', 'Group name is not changed (%s).' % group.name)

    def test_delete(self):
        """
        Test to delete group and if can't get it.
        """
        # Test to delete
        url = reverse('group delete', args=[1])
        r = self.c.post(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
        # Test to get it
        url = reverse('group', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 404, "Bad response code (%i)." % r.status_code)
