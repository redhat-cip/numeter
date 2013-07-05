from django.test import TestCase
from django.core import management
from core.models import User, Storage


class Manage_User_TestCase(TestCase):

    def test_add_user(self):
        management.call_command('add-user', username='test', email='email', password='test', superuser=True, database='default', verbosity=0)
        self.assertTrue(User.objects.all().exists(), 'No user created.')

    def test_delete_user(self):
        management.call_command('add-user', username='test', email='email', password='test', superuser=True, database='default', verbosity=0)
        management.call_command('del-user', username='test', database='default', verbosity=0)
        self.assertFalse(User.objects.all().exists(), 'User exists ever.')


class Manage_Storage_TestCase(TestCase):

    def test_add_storage(self):
        management.call_command('add-storage', alias='test', address='127.0.0.1', database='default', verbosity=0)
        self.assertTrue(Storage.objects.all().exists(), 'No storage created.')

    def test_delete_storage(self):
        management.call_command('add-storage', alias='test', address='127.0.0.1', database='default', verbosity=0)
        self.assertTrue(Storage.objects.all().exists(), 'No storage created.')
        management.call_command('del-storage', alias='test', force=True, database='default', verbosity=0)
        self.assertFalse(User.objects.all().exists(), 'Storage exists ever.')
