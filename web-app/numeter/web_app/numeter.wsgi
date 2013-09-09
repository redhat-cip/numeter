import os
import sys

EXTRA_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__)))
if EXTRA_DIR not in sys.path:
    sys.path.append(EXTRA_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = 'numeter.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
