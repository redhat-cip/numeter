"""
Tests for commands.
"""

from django.test import LiveServerTestCase
from django.core.management import call_command
from core.models import User, Storage, Host
from core.tests.utils import storage_enabled, set_storage


class Manage_User_Test(LiveServerTestCase):

    def test_add_user(self):
        """Launch 'manage.py add-user --username=test --email=email --password=test --superuser'."""
        call_command('add-user', username='test', email='email', password='test', superuser=True, graphlib='dygraph-combined.js', database='default', verbosity=0)
        self.assertTrue(User.objects.all().exists(), 'No user created.')

    def test_delete_user(self):
        """Launch 'manage.py del-user --username=test -f'."""
        call_command('add-user', username='test', email='email', password='test', superuser=True, graphlib='dygraph-combined.js', database='default', verbosity=0)
        call_command('del-user', username='test', force=True, database='default', verbosity=0)
        self.assertFalse(User.objects.all().exists(), 'User exists ever.')
