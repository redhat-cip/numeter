from __future__ import print_function

from django.test import TestCase
from django.conf import settings

from core.models import User
from core.models.utils import MediaList

from os import path, mkdir
from shutil import rmtree


class MediaField_Test(TestCase):

    def __init__(self, *args, **kwargs):
        super(MediaField_Test, self).__init__(*args, **kwargs)
        self.TEST_DIR = settings.MEDIA_ROOT + 'graphlib/'
        self.FILE1 = self.TEST_DIR + '/file1.js'
        self.TEST_SUBDIR = self.TEST_DIR + '/subdir'
        self.SUBFILE1 = self.TEST_SUBDIR + '/subfile1.js'
        self.SUBFILE2 = self.TEST_SUBDIR + '/subfile2.js'

    def setUp(self):
        rmtree(settings.MEDIA_ROOT, True)
        mkdir(settings.MEDIA_ROOT)
        mkdir(self.TEST_DIR)
        mkdir(self.TEST_SUBDIR)
        for fi in [self.FILE1,self.SUBFILE1,self.SUBFILE2]:
            with open(fi, 'w') as f:
                print("test", file=f)

    def tearDown(self):
        rmtree(settings.MEDIA_ROOT)

    # def test_update(self):
    #     pass

    def test_None(self):
        m = MediaList()
        self.assertEqual(0, len(m), 'Count %i files instead of 0.' % len(m))

    # def test_missing_file(self):
    #     pass

    def test_directory(self):
        m = MediaList(['file1.js', 'subdir'])
        files = [ i for i in m.htmlize() ]
        self.assertEqual(3, len(files), 'Count %i files instead of 3.' % len(files))

    def test_htmlize(self):
        m = MediaList(['file1.js'])
        HTML = '<script src="/media/graphlib/file1.js"></script>'
        html = [ i for i in m.htmlize() ][0]
        self.assertEqual(html, HTML, 'Not valid response "%s" should be "%s"' % (html, HTML))

    # def test_deleted_files(self):
    #     pass
