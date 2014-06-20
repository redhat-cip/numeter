"""
Tests for views which make User_Form rendering.
"""
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from core.models import User
from core.tests.utils import set_users, set_clients


class User_Test(TestCase):
    @set_users()
    @set_clients()
    def setUp(self):
        pass

    def test_get(self):
        """Get a user."""
        url = reverse('user', args=[self.admin.id])
        r = self.admin_client.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_add(self):
        """Test to get user form."""
        # Test to get form
        url = reverse('user add')
        r = self.admin_client.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
