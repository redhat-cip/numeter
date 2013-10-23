"""
Tests for source CLI management.
"""

from core.tests.utils import CmdTestCase
from core.models import Plugin, Data_Source as Source
from core.management.commands.source import Command
from core.tests.utils import storage_enabled, set_storage


class Cmd_Source_List_Test(CmdTestCase):
    """Test ``manage.py source list``."""
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        super(Cmd_Source_List_Test, self).setUp()

    def test_empty_list(self):
        """Get empty listing."""
        for s in Source.objects.all(): s.delete()
        argv = ['', 'source', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")

    def test_list(self):
        """Get listing."""
        argv = ['', 'source', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")

    def test_filtered_list(self):
        """Get filtered listing of a source."""
        PLUGIN_ID = str(Plugin.objects.all()[0].id)
        argv = ['', 'source', 'list', '-i', PLUGIN_ID]
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")


class Cmd_Source_Add_Test(CmdTestCase):
    """Test ``manage.py source add``."""
    @set_storage(extras=['host','plugin'])
    def setUp(self):
        super(Cmd_Source_Add_Test, self).setUp()

    def test_add(self):
        """Add a source."""
        DEFAULT_ID = str(Plugin.objects.all()[0].id)
        PLUGIN_SOURCES = Plugin.objects.all()[0].get_data_sources()
        argv = ['', 'source', 'add', '-i', DEFAULT_ID, '-p', PLUGIN_SOURCES[0]]
        Command().run_from_argv(argv)
        # Test creation
        new_count = Source.objects.count()
        self.assertGreater(new_count, 0, "Sources wasn't created.")

    def test_quiet_add(self):
        """Add a source without print."""
        DEFAULT_ID = str(Plugin.objects.all()[0].id)
        PLUGIN_SOURCES = Plugin.objects.all()[0].get_data_sources()
        argv = ['', 'source', 'add', '-i', DEFAULT_ID, '-p', PLUGIN_SOURCES[0], '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n" + out)

    def test_add_already_existing(self):
        """Try to add an existing plugin."""
        DEFAULT_ID = str(Plugin.objects.all()[0].id)
        Plugin.objects.all()[0].create_data_sources()
        DEFAULT_COUNT = Source.objects.count()
        argv = ['', 'source', 'add', '-i', DEFAULT_ID]
        Command().run_from_argv(argv)
        # Test creation
        new_count = Source.objects.count()
        self.assertEqual(new_count, DEFAULT_COUNT, "Sources was created again.")

    def test_add_all(self):
        """Add an host's all plugin."""
        DEFAULT_ID = str(Plugin.objects.all()[0].id)
        PLUGIN_SOURCES = Plugin.objects.all()[0].get_data_sources()
        argv = ['', 'plugin', 'add', '-i', DEFAULT_ID]
        Command().run_from_argv(argv)
        # Test creation
        new_count = Source.objects.count()
        self.assertGreater(new_count, 0, "Sources wasn't created.")
        self.assertEqual(new_count, len(PLUGIN_SOURCES), "Not all sources was created.")


class Cmd_Source_Del_Test(CmdTestCase):
    """Test ``manage.py source del``."""
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        super(Cmd_Source_Del_Test, self).setUp()

    def test_delete(self):
        """Delete a source."""
        Plugin.objects.all()[0].create_data_sources()
        DEFAULT_COUNT = Source.objects.count()
        SOURCE_ID = str(Source.objects.all()[0].id)
        argv = ['', 'source', 'del', '-i', SOURCE_ID]
        Command().run_from_argv(argv)
        # Test deletion
        new_count = Source.objects.count()
        self.assertEqual(new_count, DEFAULT_COUNT-1, "Source wasn't deleted.")

    def test_quiet_delete(self):
        """Delete a source without print."""
        Plugin.objects.all()[0].create_data_sources()
        SOURCE_ID = str(Source.objects.all()[0].id)
        argv = ['', 'source', 'del', '-i', SOURCE_ID, '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)
