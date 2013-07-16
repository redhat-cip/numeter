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

    def tearDown(self):
        Host.objects.all().delete()

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
    def test_get_unsaved_hosts(self):
        self.storage._update_hosts()
        initial_count = Host.objects.count()
        if not initial_count:
            self.skipTest("There's no host in storage.")

        Host.objects.all()[0].delete()
        unsaved_hosts = self.storage._get_unsaved_hosts()
        self.assertEqual(len(unsaved_hosts), 1, "Supposed to have 1 unsaved host (%i)" % len(unsaved_hosts))

    @storage_enabled()
    def test_get_saved_hosts(self):
        self.storage._update_hosts()
        initial_count = Host.objects.count()

        Host.objects.create(name='test', hostid='testid', storage=self.storage)
        unfoundable_hosts = self.storage._get_unfoundable_hosts()
        self.assertEqual(len(unfoundable_hosts), 1, "Supposed to have 1 unfoundable host (%i)" % len(unfoundable_hosts))
