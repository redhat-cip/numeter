"""
Dynamic settings file for site customization.
"""

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

# Little hack to disable caching
if config.getboolean_d('cache', 'use_cache', False):
    cache_backend = 'django.core.cache.backends.memcached.MemcachedCache'
else:
    cache_backend = 'django.core.cache.backends.dummy.DummyCache'

CACHES = {
    'default': {
        'BACKEND': cache_backend,
        'LOCATION': config.get('cache', 'location'),
        'TIMEOUT': config.getint_d('cache', 'timeout', 300),
        'OPTIONS': {
            'MAX_ENTRIES': config.getint_d('cache', 'max_entries', 1000),
        }
    }
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'storage': {
            'format': '[%(asctime)s] "STORAGE-GET %(message)s"',
            'datefmt' : '%d/%b/%Y %H:%M:%S'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'storage': {
            'storage': 'storage',
        }
    },
    'handlers': {
        'console':{
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'storage',
            'filters': ['storage']
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'storage': {
            'handlers': ['console'],
            'level': 'INFO',
            'filters': ['storage']
        }
    }
}

if config.getboolean_d('logging', 'use_logging', False):
    LOGGING['handlers']['info_file'] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': config.get_d('logging', 'info_file', '/var/log/numeter/webapp/info.log'),
        'maxBytes': config.getint_d('logging', 'file_size', 1000000),
        'formatter': 'verbose',
        'filters': ['storage']
    }
    LOGGING['handlers']['error_file'] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': config.get_d('logging', 'error_file', '/var/log/numeter/webapp/error.log'),
        'maxBytes': config.getint_d('logging', 'file_size', 1000000),
        'formatter': 'verbose',
        'filters': ['storage']
    }
    LOGGING['loggers']['storage']['handlers'].append('info_file')
    LOGGING['loggers']['django.request']['handlers'].append('error_file')

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = config.getobj_d('global', 'allowed_hosts', ['*'])

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = config.get_d('global', 'timezone', None)

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

# Set STATIC ROOT
if DEBUG:
    STATICFILES_DIRS = ( os.path.join(BASEDIR, '../static'), )
    STATIC_ROOT = ''
else:
    STATIC_ROOT = os.path.join(BASEDIR, '../static')



from django.conf import settings
INSTALLED_APPS = settings.INSTALLED_APPS

# Mock storage
if config.getboolean_d('debug', 'use_mock_storage', False):
    INSTALLED_APPS = INSTALLED_APPS+('mock_storage',)

## Custom configuration
# Debug Tool Bar
try:
    import debug_toolbar
except ImportError:
    pass
else:
    if config.getboolean_d('debug', 'use_debug_toolbar', False) and DEBUG:
        INSTALLED_APPS = INSTALLED_APPS+('debug_toolbar',)
        INTERNAL_IPS = ('127.0.0.1','192.168.100.1')
        MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES+('debug_toolbar.middleware.DebugToolbarMiddleware',)
        DEBUG_TOOLBAR_CONFIG = {
          'INTERCEPT_REDIRECTS': False
        }
