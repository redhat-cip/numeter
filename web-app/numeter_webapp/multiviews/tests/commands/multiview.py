"""
Tests for multiview CLI management.
"""

from core.tests.utils import CmdTestCase, set_storage
from core.models import Storage, Plugin, Data_Source as Source
from core.tests.utils import set_storage
from multiviews.models import View, Multiview
from multiviews.management.commands.multiview import Command
from multiviews.tests.utils import create_view, create_multiview


class Cmd_Multiview_List_Test(CmdTestCase):
    """Test ``manage.py multiview list``."""
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        super(Cmd_Multiview_List_Test, self).setUp()

    def test_empty_list(self):
        """Get empty listing."""
        argv = ['', 'multiview', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")
        self.assertIn("Count: 0", out, "Output isn't showing total count.")

    def test_list(self):
        """Get listing."""
        self.multiview = create_multiview()
        argv = ['', 'multiview', 'list']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertTrue(out, "No output.")
        self.assertIn("Count: 1", out, "Output isn't showing total count.")


class Cmd_Multiview_Add_Test(CmdTestCase):
    """Test ``manage.py multiview add``."""
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        super(Cmd_Multiview_Add_Test, self).setUp()

    def test_add(self):
        """Add a multiview."""
        create_view() ; create_view()
        view_ids = ','.join([ str(v.id) for v in View.objects.all()[:2] ])
        argv = ['', 'multiview', 'add', '-n', 'TEST MULTIVIEW', '-V', view_ids]
        Command().run_from_argv(argv)
        # Test creation
        new_count = Multiview.objects.count()
        out = self.stdout.getvalue()
        self.assertGreater(new_count, 0, "Multiview wasn't created.")

    def test_quiet_add(self):
        """Add a multiview without print."""
        create_view() ; create_view()
        view_ids = ','.join([ str(v.id) for v in View.objects.all()[:2] ])
        argv = ['', 'multiview', 'add', '-n', 'TEST MULTIVIEW', '-V', view_ids, '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n" + out)


class Cmd_Multiview_Del_Test(CmdTestCase):
    """Test ``manage.py multiview del``."""
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        super(Cmd_Multiview_Del_Test, self).setUp()

    def test_delete(self):
        """Delete a multiview."""
        create_view() ; create_view()
        self.multiview = create_multiview()
        argv = ['', 'multiview', 'del', '-i', str(self.multiview.id)]
        Command().run_from_argv(argv)
        # Test deletion
        new_count = Multiview.objects.count()
        self.assertEqual(new_count, 0, "Multiview wasn't deleted.")

    def test_delete_several(self):
        """Delete a several multiviews."""
        create_view() ; create_view()
        create_multiview() ; create_multiview()
        IDS  = ','.join([ str(m.id) for m in Multiview.objects.all() ])
        argv = ['', 'multiview', 'del', '-i', IDS]
        Command().run_from_argv(argv)
        # Test deletion
        new_count = Multiview.objects.count()
        self.assertEqual(new_count, 0, "All multiviews wasn't deleted.")

    def test_quiet_delete(self):
        """Delete a several without print."""
        create_view() ; create_view()
        multiview = create_multiview()
        argv = ['', 'multiview', 'del', '-i', str(multiview.id), '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)


class Cmd_Multiview_Mod_Test(CmdTestCase):
    """Test ``manage.py multiview mod``."""
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        super(Cmd_Multiview_Mod_Test, self).setUp()

    def test_mod(self):
        """Modify a multiview."""
        create_view() ; create_view()
        multiview = create_multiview()
        argv = ['', 'multiview', 'mod', '-i', str(multiview.id), '-n', 'NEW NAME']
        Command().run_from_argv(argv)
        # Test mod
        multiview = Multiview.objects.get(id=multiview.id)
        self.assertEqual(multiview.name, 'NEW NAME', "Multiview's name wasn't modified.")

    def test_quiet_mod(self):
        """Modify a multiview without print."""
        create_view() ; create_view()
        multiview = create_multiview()
        argv = ['', 'multiview', 'mod', '-i', str(multiview.id), '-n', 'NEW NAME', '-q']
        Command().run_from_argv(argv)
        # Test stdout
        out = self.stdout.getvalue()
        self.assertFalse(out, "Output is printed:\n"+out)

    def test_add_views(self):
        """Add views to a multiview."""
        create_view() ; create_view()
        multiview = create_multiview()
        multiview_view_ids = [ v.id for v in multiview.views.all() ]
        default_count = len(multiview_view_ids)
        # Set new views
        views = View.objects.exclude(id__in=multiview_view_ids)[:2]
        view_ids = ','.join([ str(s.id) for s in views ])
        argv = ['', 'multiview', 'mod', '-i', str(multiview.id), '--add-views', view_ids ]
        Command().run_from_argv(argv)
        # Test mod
        multiview = Multiview.objects.get(id=multiview.id)
        new_count = multiview.views.count()
        self.assertLess(default_count, new_count, "Views wasn't added.")

    def test_rm_views(self):
        """Remove views from a multiview."""
        create_view() ; create_view()
        multiview = create_multiview()
        view_ids = ','.join([ str(v.id) for v in multiview.views.all()[:1] ])
        default_count = multiview.views.count()
        argv = ['', 'multiview', 'mod', '-i', str(multiview.id), '--rm-views', view_ids ]
        Command().run_from_argv(argv)
        # Test mod
        multiview = Multiview.objects.get(id=multiview.id)
        new_count = multiview.views.count()
        self.assertGreater(default_count, new_count, "Views wasn't removed.")

    def test_add_views(self):
        """Add view to a multiview."""
        create_view() ; create_view()
        multiview = create_multiview()
        multiview_view_ids = [ v.id for v in multiview.views.all() ]
        default_count = len(multiview_view_ids)
        # Set new views
        views = View.objects.exclude(id__in=multiview_view_ids)[:2]
        view_ids = ','.join([ str(s.id) for s in views ])
        argv = ['', 'multiview', 'mod', '-i', str(multiview.id), '--add-views', view_ids ]
        Command().run_from_argv(argv)
        # Test mod
        multiview = Multiview.objects.get(id=multiview.id)
        new_count = multiview.views.count()
        self.assertLess(default_count, new_count, "Views wasn't added.")

    def test_rm_views(self):
        """Remove views from a multiview."""
        create_view() ; create_view()
        multiview = create_multiview()
        view_ids = ','.join([ str(v.id) for v in multiview.views.all()[:1] ])
        default_count = multiview.views.count()
        argv = ['', 'multiview', 'mod', '-i', str(multiview.id), '--rm-views', view_ids ]
        Command().run_from_argv(argv)
        # Test mod
        multiview = Multiview.objects.get(id=multiview.id)
        new_count = multiview.views.count()
        self.assertGreater(default_count, new_count, "Views wasn't removed.")
