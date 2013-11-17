"""
Settings used in testing.
"""

from core.utils.configparser import Custom_ConfigParser
config = Custom_ConfigParser()
config.read('/etc/numeter/numeter_webapp.cfg')

import os
BASEDIR = os.path.dirname(os.path.abspath(__file__))

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
TEST_STORAGES = []
if config.get_d('test', 'storage1_address', False):
    TEST_STORAGES.append({
      'name': 'Test Storage 1',
      'address': config.get_d('test', 'storage1_address', 'localhost'),
      'port': config.get_d('test', 'storage1_port', 8080),
      'url_prefix': config.get_d('test', 'storage1_url_prefix', '/numeter-storage'),
      'login': config.get_d('test', 'storage1_login', None),
      'password': config.get_d('test', 'storage1_password', None)
    })
if config.get_d('test', 'storage2_address', False):
    TEST_STORAGES.append({
      'name': 'Test Storage 2',
      'address': config.get_d('test', 'storage2_address', 'localhost'),
      'port': config.get_d('test', 'storage2_port', 8080),
      'url_prefix': config.get_d('test', 'storage2_url_prefix', '/numeter-storage'),
      'login': config.get_d('test', 'storage2_login', None),
      'password': config.get_d('test', 'storage2_password', None)
    })

# Temporary media files
BASE_MEDIA_ROOT = config.get_d('global', 'media_root', (BASEDIR+'/../media/'))
MEDIA_ROOT = config.get_d('test', 'media_root', '/tmp/numeter-media/')

# Set Liveserver, usefull for mock storage
os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'localhost:8081'

# Create temp media folder
from os import mkdir
try: mkdir(MEDIA_ROOT)
except OSError: pass
try: mkdir(MEDIA_ROOT + 'graphlib/')
except OSError: pass
