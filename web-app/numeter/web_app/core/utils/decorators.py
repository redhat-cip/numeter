from django.http import HttpResponseNotAllowed, Http404
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.utils.decorators import available_attrs

import logging
from functools import wraps

logger = logging.getLogger('django.request')

def is_ajax():
    """
    Restrict views to AJAX requests.
    Raise 404 if isn't.
    """
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(request, *args, **kwargs):
            if request.is_ajax and not settings.DEBUG:
                logger.warning("Request isn't AJAX.",
                    extra={
                        'status_code': 405,
                        'request': request
                    }   
                )   
                raise Http404
            return func(request, *args, **kwargs)
        return inner
    return decorator


def login_required():
    """Custom login_required decorator."""
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(request, *args, **kwargs):
            if not request.user.is_authenticated():
                return redirect_to_login(request.get_full_path())
            return func(request, *args, **kwargs)
        return inner
    return decorator


def superuser_only():
    """Raise 404 if user isn't superuser."""
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(request, *args, **kwargs):
            if not request.user.is_superuser:
                raise Http404("User isn't superuser.")
            return func(request, *args, **kwargs)
        return inner
    return decorator
