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
        self.assertEqual(0, len(m.file_names()), 'Count %i files instead of 0.' % len(m.file_names()))

    # def test_missing_file(self):
    #     pass

    def test_directory(self):
        """List files."""
        m = MediaList('dygraph')
        files = [ i for i in m.htmlize() ]
        self.assertEqual(2, len(files), 'Count %i files instead of 2.' % len(files))

    def test_htmlize(self):
        """Make html tags to import folder."""
        m = MediaList('dygraph')
        HTML_TO_FIND = '<script src="/media/graphlib/dygraph/subfile2.js"></script>'
        html = ''.join([ i for i in m.htmlize() ])
        self.assertIn(HTML_TO_FIND, html, "Not find '%s' in '%s'." % (HTML_TO_FIND, html))

    # def test_deleted_files(self):
    #     pass
