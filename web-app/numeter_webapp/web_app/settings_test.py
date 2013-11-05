"""
Settings used in testing.
"""

# Disable logger
import logging
logging.disable(logging.CRITICAL)

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': '/tmp/test_numeter.sqlite',
    'USER': '',
    'PASSWORD': '',
    'HOST': '',
    'PORT': '',
  }
}

# Use it as below
# Storage.objects.create(**settings.TEST_STORAGE)
TEST_STORAGE = {
  'name': 'Demo',
  'address': 'demo.numeter.com',
  'port': 8080,
  'url_prefix': '/numeter-storage',
  'login': '',
  'password': ''
}

# Disable logger
import logging
logger = logging.getLogger('storage')
logger.setLevel(10)

# Temporary media files
# DO NOT SET AS PRODUCTION MEDIA_ROOT
MEDIA_ROOT = '/tmp/numeter-media/'

# Set Liveserver, usefull for mock storage
import os
os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'localhost:8081'

### VALIDATION
from os import mkdir
from shutil import rmtree
import socket

try :
    rmtree(MEDIA_ROOT, True)
    mkdir(MEDIA_ROOT)
    mkdir(MEDIA_ROOT+'/graphlib')
    with open(MEDIA_ROOT+'/graphlib/dygraph-combined.js', 'w') as f:
        f.write('test')
except:
    pass
