DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
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
  'name': 'Numeter Demo',
  'address': 'demo.numeter.com',
  'port': 8080,
  'url_prefix': '',
  'login': '',
  'password': ''
}
