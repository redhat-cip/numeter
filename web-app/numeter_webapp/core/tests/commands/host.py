"""
Tests for host CLI management.
"""

from core.tests.utils import CmdTestCase
from core.models import Storage, Host, Group
from core.management.commands.host import Command
from core.tests.utils import storage_enabled, set_storage


class Cmd_Host_List_Test(CmdTestCase):
    """Test ``manage.py host list``."""
    @set_storage()
    def setUp(self):
        super(Cmd_Host_List_Test, self).setUp()

    def test_empty_list(self):
        """Get empty listing."""
        Host.objects.all().delete()
        cmd = Command()
        argv = ['', 'host', 'list']
        cmd.run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")

    def test_list(self):
        """Get listing."""
        cmd = Command()
        argv = ['', 'host', 'list']
        cmd.run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")


class Cmd_Host_Add_Test(CmdTestCase):
    """Test ``manage.py host add``."""
    @set_storage(extras=['host'])
    def setUp(self):
        super(Cmd_Host_Add_Test, self).setUp()

    def test_add(self):
        """Add a host."""
        DEFAULT_ID = Host.objects.all()[0].hostid
        Host.objects.all()[0].delete()
        DEFAULT_COUNT = Host.objects.count()
        cmd = Command()
        argv = ['', 'host', 'add', '-i', DEFAULT_ID]
        cmd.run_from_argv(argv)
        # Test creation
        new_count = Host.objects.count()
        self.assertEqual(new_count, DEFAULT_COUNT+1, "Host wasn't created.")

    def test_quiet_add(self):
        """Add a host without print."""
        DEFAULT_COUNT = Host.objects.count()
        DEFAULT_ID = Host.objects.all()[0].hostid
        cmd = Command()
        argv = ['', 'host', 'add', '-i', DEFAULT_ID]
        cmd.run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed.")

    def test_add_already_existing(self):
        """Try to add an existing host."""
        DEFAULT_COUNT = Host.objects.count()
        DEFAULT_ID = Host.objects.all()[0].hostid
        cmd = Command()
        argv = ['', 'host', 'add', '-i', DEFAULT_ID]
        cmd.run_from_argv(argv)
        # Test creation
        new_count = Host.objects.count()
        self.assertEqual(new_count, DEFAULT_COUNT, "Host was created again.")

    def test_add_all(self):
        """Add all host."""
        for h in Host.objects.all()[:1]: h.delete()
        TOTAL_COUNT = len(Storage.objects.get_all_host_info())
        DEFAULT_COUNT = Host.objects.count()
        cmd = Command()
        argv = ['', 'host', 'add', '-a']
        cmd.run_from_argv(argv)
        # Test creation
        new_count = Host.objects.count()
        self.assertGreater(new_count, DEFAULT_COUNT, "No host was created.")
        self.assertEqual(new_count, TOTAL_COUNT, "All host wasn't created.")


class Cmd_Host_Del_Test(CmdTestCase):
    """Test ``manage.py host del``."""
    @set_storage(extras=['host'])
    def setUp(self):
        super(Cmd_Host_Del_Test, self).setUp()

    def test_delete(self):
        """Delete a storage."""
        DEFAULT_COUNT = Host.objects.count()
        host = Host.objects.all()[0]
        cmd = Command()
        argv = ['', 'storage', 'del', '-i', host.hostid ]
        cmd.run_from_argv(argv)
        # Test deletion
        new_count = Host.objects.count()
        self.assertEqual(new_count, DEFAULT_COUNT-1, "Host wasn't deleted.")

    def test_delete_all(self):
        """Delete all host."""
        IDS = ','.join([ str(h.hostid) for h in Host.objects.all() ])
        cmd = Command()
        argv = ['', 'storage', 'del', '-i', IDS ]
        # Test deletion
        cmd.run_from_argv(argv)
        self.assertFalse(Host.objects.count(), "Hosts wasn't deleted.")

    def test_quiet_delete(self):
        """Delete an host without print."""
        host = Host.objects.all()[0]
        cmd = Command()
        argv = ['', 'storage', 'del', '-i', host.hostid, '-q']
        cmd.run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed.")


class Cmd_Host_Mod_Test(CmdTestCase):
    """Test ``manage.py host mod``."""
    @set_storage(extras=['host'])
    def setUp(self):
        super(Cmd_Host_Mod_Test, self).setUp()

    def tearDown(self):
        Group.objects.all().delete()

    def test_modify(self):
        """Modify an host."""
        HOST_ID = Host.objects.all()[0].hostid
        INITIAL_GROUP = Host.objects.all()[0].group
        group = Group.objects.create(name='NEW TEST')
        cmd = Command()
        argv = ['', 'host', 'mod', '-i', HOST_ID, '-g', str(group.id)]
        cmd.run_from_argv(argv)
        # Test modification
        self.assertEqual(Host.objects.get(hostid=HOST_ID).group, group, "Host's group wasn't modified.")

    def test_modify_all(self):
        """Modify all storage."""
        IDS = ','.join([ h.hostid for h in Host.objects.all() ])
        group = Group.objects.create(name='NEW TEST')
        cmd = Command()
        argv = ['', 'storage', 'mod', '-i', IDS, '-g', str(group.id)]
        cmd.run_from_argv(argv)
        # Test modification
        for h in Host.objects.all():
            self.assertEqual(h.group, group, "Host's group wasn't modified.")

    def test_quiet_modify(self):
        """Modify an host without print."""
        HOST_ID = Host.objects.all()[0].hostid
        group = Group.objects.create(name='NEW TEST')
        cmd = Command()
        argv = ['', 'storage', 'mod', '-i', HOST_ID, '-q', '-g', str(group.id)]
        cmd.run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed.")
