"""
Tests for views which make Group_Form rendering.
"""
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.models import Group
from core.tests.utils import set_users, set_clients


class Group_Test(TestCase):
    @set_users()
    @set_clients()
    def setUp(self):
        pass

    def test_get(self):
        """Get a filled Group form."""
        url = reverse('group', args=[self.group.id])
        r = self.admin_client.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """Get an empty Group form. """
        url = reverse('group add')
        r = self.admin_client.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
