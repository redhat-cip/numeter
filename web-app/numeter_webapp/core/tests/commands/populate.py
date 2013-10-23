"""
Tests for populate command.
"""

from core.tests.utils import CmdTestCase
from core.models import Host, Plugin, Data_Source as Source
from core.management.commands.populate import Command
from core.tests.utils import set_storage


class Cmd_Populate_Test(CmdTestCase):
    """Test ``manage.py populate``."""
    @set_storage()
    def setUp(self):
        super(Cmd_Populate_Test, self).setUp()

    def test_populate(self):
        """Add all hosts, plugins and sources."""
        argv = ['', 'populate']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")
        # Test model creation
        self.assertTrue(Host.objects.all().exists(), "No host was created")
        self.assertTrue(Plugin.objects.all().exists(), "No plugin was created")
        self.assertTrue(Source.objects.all().exists(), "No source was created")
