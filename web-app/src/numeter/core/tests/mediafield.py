from __future__ import print_function

from django.test import TestCase
from django.conf import settings

from core.models import User
from core.models.fields import MediaList

from os import path, mkdir, listdir
from shutil import rmtree


class MediaField_TestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super(MediaField_TestCase, self).__init__(*args, **kwargs)
        self.TEST_DIR = settings.MEDIA_ROOT + '/graphlib/'
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

    def test_update(self):
        pass

    def test_None(self):
        pass

    def test_missing_file(self):
        pass

    def test_directory(self):
        m = MediaList(['file1.js', 'subdir'])
        files = [ i for i in m.htmlize() ]
        self.assertEqual(3, len(files), 'Count %i files instead of 3.' % len(files))

    def test_htmlize(self):
        pass

    def test_deleted_files(self):
        pass
