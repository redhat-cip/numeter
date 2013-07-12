from django.utils.decorators import available_attrs
from functools import wraps


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
