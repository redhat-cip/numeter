from __future__ import print_function

from django.test import LiveServerTestCase
from django.test.client import Client
from django.core.management import call_command
from django.conf import settings
from django.utils.decorators import available_attrs

from core.models import Storage, Host, Plugin, Data_Source as Source
from core.models import User, Group

from functools import wraps
from cStringIO import StringIO
import os
from os import path, mkdir
from shutil import rmtree
import sys


DEFAULT_STDOUT = sys.stdout
class CmdTestCase(LiveServerTestCase):
    """Custom TestCase which capture stdout in self.stdout."""
    def setUp(self):
        super(CmdTestCase, self).setUp()
        self.stdout = StringIO()
        sys.stdout = self.stdout

    def tearDown(self):
        sys.stdout = DEFAULT_STDOUT
        super(CmdTestCase, self).tearDown()

class False_HttpRequest_dict(dict):
    """Used for test POST request."""
    def getlist(self, x):
        return self.get(x, [])


def storage_enabled():
    """ 
    Test to connect to self.storage.
    Skip test if test storage is unreachable.
    """
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(self, *args, **kwargs):
            if not self.storage.is_on():
                self.skipTest("Test storage isn't reachable.")
            return func(self, *args, **kwargs)
        return inner
    return decorator


def set_storage(extras=[]):
    """
    Set storage within Mock and settings_local.py
    Set it in self.storage. Skip test if there's no storage configurated.
    extras are host, plugin or source.
    """
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(self, *args, **kwargs):
            # Use mock if installed
            if 'mock_storage' in settings.INSTALLED_APPS:
                call_command('loaddata', 'mock_storage.json', database='default', verbosity=0)
                self.storage = Storage.objects.get(pk=1)
                for model in extras:
                    call_command('loaddata', ('mock_%s.json' % model), database='default', verbosity=0)
                # Set instance as attrs
                if Host.objects.exists():
                    self.host = Host.objects.all()[0]
                    if Plugin.objects.exists():
                        self.plugin = Plugin.objects.filter(host=self.host)[0]
                        if Source.objects.exists():
                            self.source = Source.objects.filter(plugin=self.plugin)[0]
            # Use settings_local
            elif settings.TEST_STORAGES:
                # Skip if no conf
                if not settings.TEST_STORAGES:
                    self.skipTest("There's no configurated test storage(s).")
                for storage in settings.TEST_STORAGES:
                    s = Storage.objects.create(**storage)
                # Try to reach
                if not True in [ True for s in Storage.objects.all() if s.is_on() ]:
                    self.skipTest("Configured storage(s) are unreachable:\n%s" % settings.TEST_STORAGES)
                else:
                    setattr(self, 'storage', s)
                    if 'host' in extras:
                        hostids = self.storage.get_hosts().keys()
                        if not hostids:
                            self.skipTest("No hosts found in this test storage.")
                        self.host = self.storage.create_host(hostids[0])
                        if 'plugin' in extras:
                            plugins = self.host.create_plugins()
                            if not plugins:
                                self.skipTest("No plugin found in test storage.")
                            self.plugin = plugins[0]
                            if 'source' in extras:
                                sources = self.plugin.create_data_sources()
                                if not sources:
                                    self.skipTest("No source found in test storage.")
                                self.source = sources[0]
            # Skip
            else:
                self.skipTest("No test storage has been configurated.")
            # Add user and groups
            # if 'group' in extras:
            #     call_command('loaddata', 'test_groups.json', database='default', verbosity=0)
            # if 'user' in extras:
            #     call_command('loaddata', 'test_users.json', database='default', verbosity=0)
            return func(self, *args, **kwargs)
        return inner
    return decorator


def set_users():
    """ 
    Set 1 superuser and 2 users with 2 different groups.
    Set also false graphlib directory.
    """
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(self, *args, **kwargs):
            # Create user
            call_command('loaddata', 'test_groups.json', database='default', verbosity=0)
            call_command('loaddata', 'test_users.json', database='default', verbosity=0)
            self.admin = User.objects.get(pk=1)
            self.user = User.objects.get(pk=2)
            self.user2 = User.objects.get(pk=3)
            self.group = Group.objects.get(pk=1)
            # Create false graphlib
            self.TEST_DIR = settings.MEDIA_ROOT + 'graphlib/'
            self.FILE1 = self.TEST_DIR + 'file1.js'
            self.TEST_SUBDIR = self.TEST_DIR + 'dygraph/'
            self.SUBFILE1 = self.TEST_SUBDIR + 'subfile1.js'
            self.SUBFILE2 = self.TEST_SUBDIR + 'subfile2.js'
            self.TEST_EMPTYDIR = self.TEST_DIR + 'emptydir/'
            rmtree(settings.MEDIA_ROOT, True)
            mkdir(settings.MEDIA_ROOT)
            mkdir(self.TEST_DIR)
            mkdir(self.TEST_SUBDIR)
            mkdir(self.TEST_EMPTYDIR)
            for fi in [self.FILE1,self.SUBFILE1,self.SUBFILE2]:
                with open(fi, 'w') as f:
                    print("test", file=f)
            return func(self, *args, **kwargs)
        return inner
    return decorator


def set_clients():
    """ 
    Set 3 ``Client``, admin, user and anonymous.
    Use ``core.tests.utils.set_users`` before it.
    """
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(self, *args, **kwargs):
            self.admin_client = Client()
            self.admin_client.login(username='root', password='toto')
            self.user_client = Client()
            self.user_client.login(username='Client', password='toto')
            self.client = Client()
            return func(self, *args, **kwargs)
        return inner
    return decorator
