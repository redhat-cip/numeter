# Django local settings for admin customization
from core.utils.configparser import Custom_ConfigParser
config = Custom_ConfigParser()
config.read('/etc/numeter/numeter_webapp.cfg')

import os
BASEDIR = os.path.dirname(os.path.abspath(__file__))

# Use a file to get SECRET_KEY
SECRET_KEY_FILE = config.get_d('global', 'secret_key_file', '/etc/numeter/secret_key.txt')
with open(SECRET_KEY_FILE, 'r') as f:
    SECRET_KEY = f.read().strip()

DEBUG = config.getboolean_d('debug', 'debug', False)
TEMPLATE_DEBUG = DEBUG

ADMINS = config.getobj_d('global', 'admins') 
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': config.get('database', 'engine'),
        'NAME': config.get('database', 'name'),
        'USER': config.get_d('database', 'user', ''),
        'PASSWORD': config.get_d('database', 'password', ''),
        'HOST': config.get_d('database', 'host', ''),
        'PORT': config.get_d('database', 'port', ''),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': config.get('cache', 'location'),
        'TIMEOUT': config.getint_d('cache', 'timeout', 300),
        'OPTIONS': {
            'MAX_ENTRIES': config.getint_d('cache', 'max_entries', 1000),
        }
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = config.getobj_d('global', 'allowed_hosts') 

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = config.get('global', 'timezone')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = config.get('global', 'language_code')

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = config.get_d('global', 'media_root', (BASEDIR+'/../media/'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Set timeout for connection to storages
STORAGE_TIMEOUT = config.getint_d('global', 'timeout', 5)

from django.conf import settings
INSTALLED_APPS = settings.INSTALLED_APPS

# Mock storage
if config.getboolean_d('debug', 'use_mock_storage', False):
    INSTALLED_APPS = INSTALLED_APPS+('mock_storage',)

## Custom configuration
# Debug Tool Bar
if config.getboolean_d('debug', 'use_debug_toolbar', False):
    INSTALLED_APPS = INSTALLED_APPS+('debug_toolbar',)
    INTERNAL_IPS = ('127.0.0.1','192.168.100.1')
    MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES+('debug_toolbar.middleware.DebugToolbarMiddleware',)
