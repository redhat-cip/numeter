"""
Tests for plugin CLI management.
"""

from core.tests.utils import CmdTestCase
from core.models import Host, Plugin
from core.management.commands.plugin import Command
from core.tests.utils import storage_enabled, set_storage


class Cmd_Plugin_List_Test(CmdTestCase):
    """Test ``manage.py plugin list``."""
    @set_storage(extras=['host','plugin'])
    def setUp(self):
        super(Cmd_Plugin_List_Test, self).setUp()

    def test_empty_list(self):
        """Get empty listing."""
        Plugin.objects.all().delete()
        cmd = Command()
        argv = ['', 'plugin', 'list']
        cmd.run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")

    def test_list(self):
        """Get listing."""
        host = Host.objects.all()[0]
        cmd = Command()
        argv = ['', 'plugin', 'list' '-i', host.hostid]
        cmd.run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")


class Cmd_Plugin_Add_Test(CmdTestCase):
    """Test ``manage.py plugin add``."""
    @set_storage(extras=['host'])
    def setUp(self):
        super(Cmd_Plugin_Add_Test, self).setUp()

    def test_add(self):
        """Add a plugin."""
        DEFAULT_ID = Host.objects.all()[0].hostid
        HOST_PLUGINS = Host.objects.all()[0].get_plugin_list()
        cmd = Command()
        argv = ['', 'plugin', 'add', '-i', DEFAULT_ID, '-p', HOST_PLUGINS[0]]
        cmd.run_from_argv(argv)
        # Test creation
        new_count = Plugin.objects.count()
        self.assertGreater(new_count, 0, "Plugins wasn't created.")

    def test_quiet_add(self):
        """Add a plugin without print."""
        DEFAULT_ID = Host.objects.all()[0].hostid
        cmd = Command()
        argv = ['', 'plugin', 'add', '-i', DEFAULT_ID, '-q']
        cmd.run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)

    def test_add_already_existing(self):
        """Try to add an existing plugin."""
        DEFAULT_ID = Host.objects.all()[0].hostid
        Host.objects.all()[0].create_plugins()
        DEFAULT_COUNT = Plugin.objects.count()
        cmd = Command()
        argv = ['', 'plugin', 'add', '-i', DEFAULT_ID]
        cmd.run_from_argv(argv)
        # Test creation
        new_count = Plugin.objects.count()
        self.assertEqual(new_count, DEFAULT_COUNT, "Plugins was created again.")

    def test_add_all(self):
        """Add an host's all plugin."""
        DEFAULT_ID = Host.objects.all()[0].hostid
        HOST_PLUGINS = Host.objects.all()[0].get_plugin_list()
        cmd = Command()
        argv = ['', 'plugin', 'add', '-i', DEFAULT_ID]
        cmd.run_from_argv(argv)
        # Test creation
        new_count = Plugin.objects.count()
        self.assertGreater(new_count, 0, "Plugins wasn't created.")
        self.assertEqual(new_count, len(HOST_PLUGINS), "Not all plugins was created.")


class Cmd_Plugin_Del_Test(CmdTestCase):
    """Test ``manage.py plugin del``."""
    @set_storage(extras=['host'])
    def setUp(self):
        super(Cmd_Plugin_Del_Test, self).setUp()

    def test_delete(self):
        """Delete a plugin."""
        host = Host.objects.all()[0].create_plugins()
        DEFAULT_COUNT = Plugin.objects.count()
        PLUGIN_ID = str(Plugin.objects.all()[0].id)
        cmd = Command()
        argv = ['', 'plugin', 'del', '-i', PLUGIN_ID]
        cmd.run_from_argv(argv)
        # Test deletion
        new_count = Plugin.objects.count()
        self.assertEqual(new_count, DEFAULT_COUNT-1, "Plugin wasn't deleted.")

    def test_quiet_delete(self):
        """Delete a plugin without print."""
        host = Host.objects.all()[0].create_plugins()
        PLUGIN_ID = str(Plugin.objects.all()[0].id)
        cmd = Command()
        argv = ['', 'plugin', 'del', '-i', PLUGIN_ID, '-q']
        cmd.run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)
