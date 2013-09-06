from django.core import management
from django.conf import settings
from django.utils.decorators import available_attrs
from core.models import Storage, Host
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
                    self.storage._update_hosts()
            # Skip
            else:
                self.skipTest("No test storage has been configurated.")

            return func(self, *args, **kwargs)
        return inner
    return decorator


