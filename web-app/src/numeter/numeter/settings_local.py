# Django local settings for admin customization

from django.conf import settings
INSTALLED_APPS = settings.INSTALLED_APPS

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql' or 'oracle'.
        'NAME': '/tmp/numeter.sqlite',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.4/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/var/www/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Debug Tool Bar
INSTALLED_APPS = INSTALLED_APPS+('debug_toolbar',)
if 'debug_toolbar' in INSTALLED_APPS :
    INTERNAL_IPS = ('127.0.0.1','192.168.100.1')
    MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES+('debug_toolbar.middleware.DebugToolbarMiddleware',)

# Django Extensions
#INSTALLED_APPS = INSTALLED_APPS+('django_extensions',)
