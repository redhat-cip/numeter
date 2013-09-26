from django.core import management
from django.conf import settings
from django.utils.decorators import available_attrs
from core.models import Storage, Host
from core.models import User, Group
from functools import wraps


class False_HttpRequest_dict(dict):
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
    """
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(self, *args, **kwargs):
            # Use mock if installed
            if 'mock_storage' in settings.INSTALLED_APPS:
                management.call_command('loaddata', 'mock_storage.json', database='default', verbosity=0)
                self.storage = Storage.objects.get(pk=1)
                for model in extras:
                    management.call_command('loaddata', ('mock_%s.json' % model), database='default', verbosity=0)
            # Use settings_local
            elif settings.TEST_STORAGE['address']:
                self.storage = Storage.objects.create(**settings.TEST_STORAGE)
                if not self.storage.is_on():
                    self.skipTest("Configured storage unreachable.")
                else:
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

            return func(self, *args, **kwargs)
        return inner
    return decorator


def set_users():
    """ 
    Set 1 superuser and 2 users with 2 different groups.
    """
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(self, *args, **kwargs):
            management.call_command('loaddata', 'test_groups.json', database='default', verbosity=0)
            management.call_command('loaddata', 'test_users.json', database='default', verbosity=0)
            self.admin = User.objects.get(pk=1)
            self.user = User.objects.get(pk=2)
            self.user2 = User.objects.get(pk=3)
            self.group = Group.objects.get(pk=1)
            return func(self, *args, **kwargs)
        return inner
    return decorator
