"""
Tests for view CLI management.
"""

from core.tests.utils import CmdTestCase, set_storage
from core.models import Storage, Plugin, Data_Source as Source
from core.tests.utils import set_storage
from multiviews.models import Skeleton, View
from multiviews.management.commands.view import Command
from multiviews.tests.utils import create_view


class Cmd_View_List_Test(CmdTestCase):
    """Test ``manage.py view list``."""
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        super(Cmd_View_List_Test, self).setUp()

    def test_empty_list(self):
        """Get empty listing."""
        argv = ['', 'view', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")
        self.assertIn("Count: 0", out, "Output isn't showing total count.")

    def test_list(self):
        """Get listing."""
        self.view = create_view()
        argv = ['', 'view', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")
        self.assertIn("Count: 1", out, "Output isn't showing total count.")


class Cmd_View_Add_Test(CmdTestCase):
    """Test ``manage.py view add``."""
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        super(Cmd_View_Add_Test, self).setUp()

    def test_add(self):
        """Add a view."""
        source_ids = ','.join([ str(s.id) for s in Source.objects.all()[:2] ])
        argv = ['', 'view', 'add', '-n', 'TEST VIEW', '-s', source_ids]
        Command().run_from_argv(argv)
        # Test creation
        new_count = View.objects.count()
        out = self.stdout.getvalue()
        self.assertGreater(new_count, 0, "View wasn't created.")

    def test_quiet_add(self):
        """Add a view without print."""
        source_ids = ','.join([ str(s.id) for s in Source.objects.all()[:2] ])
        argv = ['', 'view', 'add', '-n', 'TEST VIEW', '-s', source_ids, '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n" + out)


class Cmd_View_Del_Test(CmdTestCase):
    """Test ``manage.py view del``."""
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        super(Cmd_View_Del_Test, self).setUp()

    def test_delete(self):
        """Delete a view."""
        self.view = create_view()
        argv = ['', 'view', 'del', '-i', str(self.view.id)]
        Command().run_from_argv(argv)
        # Test deletion
        new_count = View.objects.count()
        self.assertEqual(new_count, 0, "View wasn't deleted.")

    def test_delete_several(self):
        """Delete a several views."""
        create_view() ; create_view()
        IDS  = ','.join([ str(s.id) for s in View.objects.all() ])
        argv = ['', 'view', 'del', '-i', IDS]
        Command().run_from_argv(argv)
        # Test deletion
        new_count = View.objects.count()
        self.assertEqual(new_count, 0, "All views wasn't deleted.")

    def test_quiet_delete(self):
        """Delete a several without print."""
        view = create_view()
        argv = ['', 'view', 'del', '-i', str(view.id), '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)


class Cmd_View_Mod_Test(CmdTestCase):
    """Test ``manage.py view mod``."""
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        super(Cmd_View_Mod_Test, self).setUp()

    def test_mod(self):
        """Modify a view."""
        view = create_view()
        argv = ['', 'view', 'mod', '-i', str(view.id), '-n', 'NEW NAME']
        Command().run_from_argv(argv)
        # Test mod
        view = View.objects.get(id=view.id)
        self.assertEqual(view.name, 'NEW NAME', "View's name wasn't modified.")

    def test_quiet_mod(self):
        """Modify a view without print."""
        view = create_view()
        argv = ['', 'view', 'mod', '-i', str(view.id), '-n', 'NEW NAME', '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)

    def test_add_sources(self):
        """Add sources to a view."""
        view = create_view()
        view_source_ids = [ v.id for v in view.sources.all() ]
        default_count = len(view_source_ids)
        # Set new sources
        sources = Source.objects.exclude(id__in=view_source_ids)[:2]
        source_ids = ','.join([ str(s.id) for s in sources ])
        argv = ['', 'view', 'mod', '-i', str(view.id), '--add-sources', source_ids ]
        Command().run_from_argv(argv)
        # Test mod
        view = View.objects.get(id=view.id)
        new_count = view.sources.count()
        self.assertLess(default_count, new_count, "Sources wasn't added.")

    def test_rm_sources(self):
        """Remove sources from a view."""
        view = create_view()
        source_ids = ','.join([ str(v.id) for v in view.sources.all()[:1] ])
        default_count = view.sources.count()
        argv = ['', 'view', 'mod', '-i', str(view.id), '--rm-sources', source_ids ]
        Command().run_from_argv(argv)
        # Test mod
        view = View.objects.get(id=view.id)
        new_count = view.sources.count()
        self.assertGreater(default_count, new_count, "Sources wasn't removed.")
