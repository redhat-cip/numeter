"""
Tests for storage CLI management.
"""

from core.tests.utils import CmdTestCase
from core.models import Storage
from core.management.commands.storage import Command
from core.tests.utils import storage_enabled, set_storage


class Cmd_Storage_List_Test(CmdTestCase):
    """Test ``manage.py storage list``."""
    @set_storage()
    def setUp(self):
        super(Cmd_Storage_List_Test, self).setUp()

    def test_empty_list(self):
        """Get empty listing."""
        Storage.objects.all().delete()
        argv = ['', 'storage', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")

    def test_list(self):
        """Get listing."""
        argv = ['', 'storage', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")


class Cmd_Storage_Add_Test(CmdTestCase):
    """Test ``manage.py storage add``."""
    @set_storage()
    def setUp(self):
        super(Cmd_Storage_Add_Test, self).setUp()

    def test_add(self):
        """Add a storage."""
        DEFAULT_COUNT = Storage.objects.count()
        argv = ['', 'storage', 'add', '-a', 'localhost']
        Command().run_from_argv(argv)
        # Test creation
        new_count = Storage.objects.count()
        self.assertEqual(new_count, DEFAULT_COUNT+1, "Storage wasn't created.")

    def test_quiet_add(self):
        """Add a storage whitout print."""
        argv = ['', 'storage', 'add', '-a', 'localhost', '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)


class Cmd_Storage_Del_Test(CmdTestCase):
    """Test ``manage.py storage del``."""
    @set_storage()
    def setUp(self):
        super(Cmd_Storage_Del_Test, self).setUp()

    def test_delete(self):
        """Delete a storage."""
        DEFAULT_COUNT = Storage.objects.count()
        argv = ['', 'storage', 'del', '-i', str(self.storage.id)]
        Command().run_from_argv(argv)
        # Test deletion
        new_count = Storage.objects.count()
        self.assertEqual(new_count, DEFAULT_COUNT-1, "Storage wasn't deleted.")

    def test_delete_all(self):
        """Delete all storage."""
        IDS = ','.join([ str(s.id) for s in Storage.objects.all() ])
        argv = ['', 'storage', 'del', '-i', IDS ]
        # Test deletion
        Command().run_from_argv(argv)
        self.assertFalse(Storage.objects.count(), "Storages wasn't deleted.")

    def test_quiet_delete(self):
        """Delete a storage without print."""
        argv = ['', 'storage', 'del', '-i', str(self.storage.id), '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)


class Cmd_Storage_Mod_Test(CmdTestCase):
    """Test ``manage.py storage mod``."""
    @set_storage()
    def setUp(self):
        super(Cmd_Storage_Mod_Test, self).setUp()

    def test_modify(self):
        """Modify a storage."""
        STORAGE_ID = Storage.objects.all()[0].id
        argv = ['', 'storage', 'mod', '-i', str(self.storage.id), '--name=TEST']
        Command().run_from_argv(argv)
        # Test modification
        new_name = Storage.objects.get(id=STORAGE_ID).name
        self.assertEqual(new_name, 'TEST', "Storage's name wasn't modified.")

    def test_modify_all(self):
        """Modify all storage."""
        IDS = ','.join([ str(s.id) for s in Storage.objects.all() ])
        argv = ['', 'storage', 'mod', '-i', IDS, '--address=TEST']
        Command().run_from_argv(argv)
        # Test modification
        for s in Storage.objects.all():
            self.assertEqual(s.address, 'TEST', "Storage's name wasn't modified.")

    def test_quiet_modify(self):
        """Modify a storage without print."""
        argv = ['', 'storage', 'mod', '-i', str(self.storage.id), '-q', '--address=TEST']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)
