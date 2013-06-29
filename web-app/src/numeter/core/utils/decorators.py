from django.http import HttpResponseNotAllowed, Http404
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.utils.decorators import available_attrs

import logging
from functools import wraps

logger = logging.getLogger('django.request')

def is_ajax():
    """ 
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
    """ 
    """
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(request, *args, **kwargs):
            if not request.user.is_authenticated():
                return redirect_to_login(request.get_full_path())
            return func(request, *args, **kwargs)
        return inner
    return decorator
