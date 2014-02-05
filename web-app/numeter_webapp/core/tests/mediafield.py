from django.test import TestCase
from django.conf import settings

from core.models import User
from core.models.utils import MediaList
from core.tests.utils import set_users

from shutil import rmtree


class MediaField_Test(TestCase):
    @set_users()
    def setUp(self):
        pass

    def tearDown(self):
        rmtree(settings.MEDIA_ROOT)

    # def test_update(self):
    #     pass

    def test_None(self):
        """List files in empty directory."""
        m = MediaList('emptydir')
        self.assertEqual(0, len(m.get_files()), 'Count %i files instead of 0.' % len(m.get_files()))

    # def test_missing_file(self):
    #     pass

    def test_walk(self):
        """List files."""
        m = MediaList('dygraph')
        files = [ i for i in m._walk() ]
        self.assertEqual(2, len(files), 'Count %i files instead of 2.' % len(files))

    # def test_deleted_files(self):
    #     pass
