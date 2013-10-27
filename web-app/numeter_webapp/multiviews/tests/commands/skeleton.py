"""
Tests for skeleton CLI management.
"""

from core.tests.utils import CmdTestCase, set_storage
from core.models import Storage, Plugin, Data_Source as Source
from multiviews.models import Skeleton, View
from multiviews.management.commands.skeleton import Command


class Cmd_Skeleton_List_Test(CmdTestCase):
    """Test ``manage.py skeleton list``."""
    def test_empty_list(self):
        """Get empty listing."""
        argv = ['', 'skeleton', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")
        self.assertIn("Count: 0", out, "Output isn't showing total count.")

    def test_list(self):
        """Get listing."""
        skeleton = Skeleton.objects.create(name='TEST SKELETON', plugin_pattern='.', source_pattern='.')
        argv = ['', 'skeleton', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")
        self.assertIn("Count: 1", out, "Output isn't showing total count.")


class Cmd_Skeleton_Add_Test(CmdTestCase):
    """Test ``manage.py skeleton add``."""
    def test_add(self):
        """Add a skeleton."""
        argv = ['', 'skeleton', 'add', '-n', 'TEST SKELETON', '-p', '.', '-s', '.']
        Command().run_from_argv(argv)
        # Test creation
        new_count = Skeleton.objects.count()
        self.assertGreater(new_count, 0, "Skeleton wasn't created.")

    def test_quiet_add(self):
        """Add a skeleton without print."""
        argv = ['', 'skeleton', 'add', '-n', 'TEST SKELETON', '-p', '.', '-s', '.', '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n" + out)

    def test_add_already_existing(self):
        """Try to add an existing skeleton."""
        skeleton = Skeleton.objects.create(name='TEST SKELETON', plugin_pattern='.', source_pattern='.')
        argv = ['', 'skeleton', 'add', '-n', 'TEST SKELETON', '-p', '.', '-s', '.']
        Command().run_from_argv(argv)
        # Test creation
        new_count = Skeleton.objects.count()
        self.assertEqual(new_count, 1, "Skeleton was created again.")


class Cmd_Skeleton_Del_Test(CmdTestCase):
    """Test ``manage.py skeleton del``."""
    def test_delete(self):
        """Delete a skeleton."""
        skeleton = Skeleton.objects.create(name='TEST SKELETON', plugin_pattern='.', source_pattern='.')
        argv = ['', 'skeleton', 'del', '-i', str(skeleton.id)]
        Command().run_from_argv(argv)
        # Test deletion
        new_count = Skeleton.objects.count()
        self.assertEqual(new_count, 0, "Skeleton wasn't deleted.")

    def test_delete_several(self):
        """Delete a several group."""
        skeleton = Skeleton.objects.create(name='TEST SKELETON', plugin_pattern='.', source_pattern='.')
        skeleton = Skeleton.objects.create(name='TEST SKELETON2', plugin_pattern='.', source_pattern='.')
        IDS  = ','.join([ str(s.id) for s in Skeleton.objects.all() ])
        argv = ['', 'skeleton', 'del', '-i', IDS]
        Command().run_from_argv(argv)
        # Test deletion
        new_count = Skeleton.objects.count()
        self.assertEqual(new_count, 0, "All skeletons wasn't deleted.")

    def test_quiet_delete(self):
        """Delete a several without print."""
        skeleton = Skeleton.objects.create(name='TEST SKELETON', plugin_pattern='.', source_pattern='.')
        argv = ['', 'skeleton', 'del', '-i', str(skeleton.id), '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)


class Cmd_Skeleton_Mod_Test(CmdTestCase):
    """Test ``manage.py skeleton mod``."""
    def test_mod(self):
        """Modify a group."""
        skeleton = Skeleton.objects.create(name='TEST SKELETON', plugin_pattern='.', source_pattern='.')
        argv = ['', 'skeleton', 'mod', '-i', str(skeleton.id), '-n', 'NEW NAME']
        Command().run_from_argv(argv)
        # Test deletion
        skeleton = Skeleton.objects.get(id=skeleton.id)
        self.assertEqual(skeleton.name, 'NEW NAME', "Skeleton's name wasn't modified.")

    def test_quiet_delete(self):
        """Modify a skeleton without print."""
        skeleton = Skeleton.objects.create(name='TEST SKELETON', plugin_pattern='.', source_pattern='.')
        argv = ['', 'skeleton', 'mod', '-i', str(skeleton.id), '-n', 'NEW NAME', '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)

class Cmd_Skeleton_Create_View_Test(CmdTestCase):
    """Test ``manage.py skeleton create_view``."""
    @set_storage()
    def setUp(self):
        super(Cmd_Skeleton_Create_View_Test, self).setUp()
        self.hostid = Storage.objects.all()[0].create_hosts()[0].hostid
        self.plugin = Storage.objects.all()[0].get_plugins_raw(self.hostid).keys()[0]
        self.source = Storage.objects.all()[0].get_plugin_data_sources(self.hostid, self.plugin)[0]

    def test_create_view(self):
        """Create view, plugin and source ."""
        skeleton = Skeleton.objects.create(name='TEST SKELETON', plugin_pattern=self.plugin, source_pattern=self.source)
        argv = ['', 'skeleton', 'create_view', '-i', str(skeleton.id), '-I', self.hostid, '-n', 'TEST VIEW']
        Command().run_from_argv(argv)
        # Test
        self.assertTrue(Plugin.objects.exists(), "Plugin wasn't created.")
        self.assertTrue(Source.objects.exists(), "Source wasn't created.")
        self.assertTrue(View.objects.exists(), "No new view.")
