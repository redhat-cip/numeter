from django.utils.decorators import available_attrs
from rest_framework.test import APIClient
from functools import wraps

LOGIN_URL = '/auth/login/'


def set_clients():
    """ 
    Set 3 ``APIClient``, admin, user and anonymous.
    Use ``core.tests.utils.set_users`` before it.
    """
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(self, *args, **kwargs):
            self.admin_client = APIClient()
            self.admin_client.post(LOGIN_URL, {'username':self.admin.username, 'password':'toto'})
            self.user_client = APIClient()
            self.user_client.post(LOGIN_URL, {'username':self.user.username, 'password':'toto'})
            self.client = APIClient()
            return func(self, *args, **kwargs)
        return inner
    return decorator
