from django.test import TestCase
from django.core import management
from django.conf import settings

from core.models import Storage, Host
from core.tests.utils import storage_enabled


class Storage_TestCase(TestCase):
    fixtures = ['test_storage.json']

    def setUp(self):
        if settings.TEST_STORAGE['address']:
            self.storage = Storage.objects.create(**settings.TEST_STORAGE)
        elif 'mock_storage' in settings.INSTALLED_APPS:
            management.call_command('loaddata', 'mock_storage.json', database='default', verbosity=0)
            self.storage = Storage.objects.get(pk=1)
        else:
            self.skipTest('No test storage has been configurated.')

    @storage_enabled()
    def test_proxy(self):
        url = 'http://%s:%s/numeter-storage/list' % (self.storage.address, self.storage.port)
        r = self.storage.proxy.open(url)
        self.assertEqual(r.code, 200, "Bad response code (%i)." % r.code)

    @storage_enabled()
    def test_get_hosts(self):
        hosts_dict = self.storage.get_hosts()
        self.assertIsInstance(hosts_dict, dict, "Invalide response type, should be dict.")

    @storage_enabled()
    def test_create_host_from_storage(self):
        self.storage._update_hosts()
        hosts = Host.objects.all()
        if hosts.count():
            self.assertTrue(hosts.exists())

    @storage_enabled()
    def test_get_info(self):
        self.storage._update_hosts()
        hosts = Host.objects.all()
        if hosts.count():
            host = hosts[0]
            info = host.get_info()

    @storage_enabled()
    def test_get_info(self):
        self.storage._update_hosts()
        hosts = Host.objects.all()
        if hosts.count():
            host = hosts[0]
            info = host.get_plugins()
