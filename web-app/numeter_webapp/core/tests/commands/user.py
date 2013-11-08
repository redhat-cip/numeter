"""
Tests for user CLI management.
"""

from core.tests.utils import CmdTestCase
from core.models import User, Group
from core.management.commands.user import Command
from core.tests.utils import set_users, set_storage


class Cmd_User_List_Test(CmdTestCase):
    """Test ``manage.py user list``."""
    def test_empty_list(self):
        """Get empty listing."""
        argv = ['', 'user', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")
        self.assertIn("Count: 0", out, "Output isn't showing total count.")

    def test_list(self):
        """Get listing."""
        u = User.objects.create(username='TESTUSER')
        argv = ['', 'source', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")
        self.assertIn("Count: 1", out, "Output isn't showing total count.")


class Cmd_User_Add_Test(CmdTestCase):
    """Test ``manage.py user add``."""
    @set_users()
    def setUp(self):
        super(Cmd_User_Add_Test, self).setUp()
        User.objects.all().delete()

    def test_add(self):
        """Add a user."""
        argv = ['', 'user', 'add', '-u', 'TESTUSER', '-p', 'pass']
        Command().run_from_argv(argv)
        # Test creation
        new_count = User.objects.count()
        self.assertGreater(new_count, 0, "User wasn't created.")

    def test_quiet_add(self):
        """Add a user without print."""
        argv = ['', 'user', 'add', '-u', 'TEST USER', '-p', 'pass', '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n" + out)

    def test_add_already_existing(self):
        """Try to add an existing user."""
        argv = ['', 'user', 'add', '-u', 'TEST USER', '--password=pass']
        Command().run_from_argv(argv)
        Command().run_from_argv(argv)
        # Test creation
        new_count = User.objects.count()
        self.assertEqual(new_count, 1, "User was created again.")


class Cmd_User_Del_Test(CmdTestCase):
    """Test ``manage.py user del``."""
    def test_delete(self):
        """Delete a group."""
        user = User.objects.create(username='TEST USER')
        argv = ['', 'user', 'del', '-i', str(user.id)]
        Command().run_from_argv(argv)
        # Test deletion
        new_count = User.objects.count()
        self.assertEqual(new_count, 0, "User wasn't deleted.")

    def test_delete_several(self):
        """Delete a several user."""
        IDS  = ','.join([ str(User.objects.create(username=n).id) for n in 'AB' ])
        argv = ['', 'user', 'del', '-i', IDS]
        Command().run_from_argv(argv)
        # Test deletion
        new_count = User.objects.count()
        self.assertEqual(new_count, 0, "All groups wasn't deleted.")

    def test_quiet_delete(self):
        """Delete a user without print."""
        user = User.objects.create(username='TEST USER')
        argv = ['', 'user', 'del', '-i', str(user.id), '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)


class Cmd_User_Mod_Test(CmdTestCase):
    """Test ``manage.py user mod``."""
    def test_mod(self):
        """Modify a user."""
        user = User.objects.create(username='TEST USER')
        argv = ['', 'user', 'mod', '-i', str(user.id), '-u', 'NEW NAME']
        Command().run_from_argv(argv)
        # Test mod
        user = User.objects.get(id=user.id)
        self.assertEqual(user.username, 'NEW NAME', "User's name wasn't modified.")

    def test_quiet_mod(self):
        """Modify a user without print."""
        user = User.objects.create(username='TEST USER')
        argv = ['', 'user', 'mod', '-i', str(user.id), '-u', 'NEW NAME', '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)

    def test_add_groups(self):
        """Add groups to a user."""
        user = User.objects.create(username='TEST USER')
        group = Group.objects.create(name='A')
        argv = ['', 'user', 'mod', '-i', str(user.id), '--add-groups', str(group.id) ]
        Command().run_from_argv(argv)
        # Test mod
        user = User.objects.get(id=user.id)
        new_count = user.groups.count()
        self.assertEqual(1, new_count, "Group wasn't added.")

    def test_rm_groups(self):
        """Remove groups from a user."""
        group = Group.objects.create(name='A')
        user = User.objects.create(username='TEST USER')
        user.groups.add(group)
        argv = ['', 'user', 'mod', '-i', str(user.id), '--rm-groups', str(group.id) ]
        Command().run_from_argv(argv)
        # Test mod
        user = User.objects.get(id=user.id)
        new_count = user.groups.count()
        self.assertEqual(0, new_count, "Group wasn't removed.")
