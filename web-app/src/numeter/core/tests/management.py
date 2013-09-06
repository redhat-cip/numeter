from django.test import TestCase
from django.core import management
from core.models import User, Storage, Host
from core.tests.utils import storage_enabled, set_storage


class Manage_User_TestCase(TestCase):

    def test_add_user(self):
        """Launch 'manage.py add-user --username=test --email=email --password=test --superuser'."""
        management.call_command('add-user', username='test', email='email', password='test', superuser=True, graphlib='dygraph-combined.js', database='default', verbosity=0)
        self.assertTrue(User.objects.all().exists(), 'No user created.')

    def test_delete_user(self):
        """Launch 'manage.py del-user --username=test -f'."""
        management.call_command('add-user', username='test', email='email', password='test', superuser=True, graphlib='dygraph-combined.js', database='default', verbosity=0)
        management.call_command('del-user', username='test', force=True, database='default', verbosity=0)
        self.assertFalse(User.objects.all().exists(), 'User exists ever.')


class Manage_Storage_TestCase(TestCase):

    def test_add_storage(self):
        """Launch 'manage.py add-storage --alias=test --address=127.0.0.1'."""
        management.call_command('add-storage', alias='test', address='127.0.0.1', database='default', verbosity=0)
        self.assertTrue(Storage.objects.all().exists(), 'No storage created.')

    def test_delete_storage(self):
        """Launch 'manage.py del-storage --alias=test -f'."""
        management.call_command('add-storage', alias='test', address='127.0.0.1', database='default', verbosity=0)
        self.assertTrue(Storage.objects.all().exists(), 'No storage created.')
        management.call_command('del-storage', alias='test', force=True, database='default', verbosity=0)
        self.assertFalse(User.objects.all().exists(), 'Storage exists ever.')


class Manage_Repair_TestCase(TestCase):

    @set_storage(extras=['host'])
    def setUp(self):
        if Storage.objects.count() < 2:
            self.skip("Cannot do this test with less than 2 storages.")
        self.host = Host.objects.all()[0]

    def test_repair(self):
        """Launch 'manage.py repair_hosts -f'."""
        # Test cmd
        management.call_command('repair_hosts', force=True, database='default', verbosity=0)
        good_storage = self.host.storage
        bad_storage = Storage.objects.exclude(pk=good_storage.pk)[0]
        # Break and launch cmd
        self.host.storage = bad_storage
        self.host.save()
        management.call_command('repair_hosts', force=True, database='default', verbosity=0)
        self.host = Host.objects.get(pk=self.host.pk)
        self.assertEqual(self.host.storage, good_storage, "Broken host does not have been configurated.")
