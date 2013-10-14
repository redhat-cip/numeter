"""
Tests for group CLI management.
"""

from core.tests.utils import CmdTestCase
from core.models import Group, Storage, Host
from core.management.commands.group import Command
from core.tests.utils import set_storage


class Cmd_Group_List_Test(CmdTestCase):
    """Test ``manage.py group list``."""
    def test_empty_list(self):
        """Get empty listing."""
        argv = ['', 'group', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")
        self.assertIn("Count: 0", out, "Output isn't showing total count.")

    def test_list(self):
        """Get listing."""
        group = Group.objects.create(name='TEST GROUP')
        argv = ['', 'group', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")
        self.assertIn("Count: 1", out, "Output isn't showing total count.")


class Cmd_Group_Add_Test(CmdTestCase):
    """Test ``manage.py group add``."""
    def test_add(self):
        """Add a group."""
        argv = ['', 'group', 'add', '-n', 'TEST GROUP']
        Command().run_from_argv(argv)
        # Test creation
        new_count = Group.objects.count()
        self.assertGreater(new_count, 0, "Group wasn't created.")

    def test_quiet_add(self):
        """Add a group without print."""
        argv = ['', 'group', 'add', '-n', 'TEST GROUP', '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n" + out)

    def test_add_already_existing(self):
        """Try to add an existing group."""
        group = Group.objects.create(name='TEST GROUP')
        argv = ['', 'group', 'add', '-n', 'TEST GROUP', '-q']
        Command().run_from_argv(argv)
        # Test creation
        new_count = Group.objects.count()
        self.assertEqual(new_count, 1, "Group was created again.")

    def test_add_several(self):
        """Add several group."""
        argv = ['', 'group', 'add', '-n', 'GROUP1,GROUP2']
        Command().run_from_argv(argv)
        # Test creation
        new_count = Group.objects.count()
        self.assertGreater(new_count, 0, "Groups wasn't created.")
        self.assertEqual(new_count, 2, "Not all groups was created.")


class Cmd_Group_Del_Test(CmdTestCase):
    """Test ``manage.py group del``."""
    def test_delete(self):
        """Delete a group."""
        from core.models import Group
        group = Group.objects.create(name='TEST GROUP')
        argv = ['', 'group', 'del', '-i', str(group.id)]
        Command().run_from_argv(argv)
        # Test deletion
        new_count = Group.objects.count()
        self.assertEqual(new_count, 0, "Group wasn't deleted.")

    def test_delete_several(self):
        """Delete a several group."""
        IDS  = ','.join([ str(Group.objects.create(name=n).id) for n in 'AB' ])
        argv = ['', 'group', 'del', '-i', IDS]
        Command().run_from_argv(argv)
        # Test deletion
        new_count = Group.objects.count()
        self.assertEqual(new_count, 0, "All groups wasn't deleted.")

    def test_quiet_delete(self):
        """Delete a group without print."""
        group = Group.objects.create(name='TEST GROUP')
        argv = ['', 'group', 'del', '-i', str(group.id), '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)


class Cmd_Group_Mod_Test(CmdTestCase):
    """Test ``manage.py group mod``."""
    def test_mod(self):
        """Modify a group."""
        group = Group.objects.create(name='TEST GROUP')
        argv = ['', 'group', 'mod', '-i', str(group.id), '-n', 'NEW NAME']
        Command().run_from_argv(argv)
        # Test deletion
        group = Group.objects.get(id=group.id)
        self.assertEqual(group.name, 'NEW NAME', "Group's name wasn't modified.")

    def test_quiet_delete(self):
        """Modify a group without print."""
        group = Group.objects.create(name='TEST GROUP')
        argv = ['', 'group', 'mod', '-i', str(group.id), '-n', 'NEW NAME', '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)


class Cmd_Group_Hosts_Test(CmdTestCase):
    """Test ``manage.py group hosts``."""
    @set_storage(extras=['host'])
    def setUp(self):
        super(Cmd_Group_Hosts_Test, self).setUp()

    def test_empty_list(self):
        """Get empty listing."""
        Host.objects.all().delete()
        argv = ['', 'group', 'hosts']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")
        #self.assertIn("Count: 0", out, "Output isn't showing total count.")

    def test_list(self):
        """Get listing."""
        argv = ['', 'group', 'hosts']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")
        #self.assertIn("Count: 1", out, "Output isn't showing total count.")
