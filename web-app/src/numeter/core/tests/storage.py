from django.test import TestCase
from django.core import management
from django.conf import settings

from core.models import Storage, Host
from core.tests.utils import storage_enabled


class Storage_TestCase(TestCase):
    fixtures = ['test_storage.json']

    def setUp(self):
        if 'mock_storage' in settings.INSTALLED_APPS:
            management.call_command('loaddata', 'mock_storage.json', database='default', verbosity=0)
            self.storage = Storage.objects.get(pk=1)
        elif settings.TEST_STORAGE['address']:
            self.storage = Storage.objects.create(**settings.TEST_STORAGE)
            if not self.storage.is_on():
                self.skipTest("Configured storage unreachable.")
        else:
            self.skipTest("No test storage has been configurated.")

        self.storage._update_hosts()
        if not Host.objects.exists():
            self.skipTest("There's no host in storage.")

    def tearDown(self):
        Host.objects.all().delete()

    @storage_enabled()
    def test_proxy(self):
        url = "%(protocol)s://%(address)s:%(port)i%(url_prefix)s/numeter-storage/hosts" % self.storage.__dict__
        r = self.storage.proxy.open(url)
        self.assertEqual(r.code, 200, "Bad response code (%i)." % r.code)

    @storage_enabled()
    def test_get_hosts(self):
        hosts_dict = self.storage.get_hosts()
        self.assertIsInstance(hosts_dict, dict, "Invalide response type, should be dict.")

    @storage_enabled()
    def test_create_host_from_storage(self):
        self.storage.create_hosts()
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
        unfoundable_hosts = self.storage._get_unfoundable_hostids()
        self.assertEqual(len(unfoundable_hosts), 1, "Supposed to have 1 unfoundable host (%i)" % len(unfoundable_hosts))


class Storage_Manager_TestCase(TestCase):

    def setUp(self):
        if 'mock_storage' in settings.INSTALLED_APPS:
            management.call_command('loaddata', 'mock_storage.json', database='default', verbosity=0)
            self.storage1 = Storage.objects.get(pk=1)
            self.storage2 = Storage.objects.get(pk=2)
        else:
            self.skipTest("No test storage has been configurated.")

    def tearDown(self):
        Host.objects.all().delete()

    def test_unsaved_hosts(self):
        self.storage1._update_hosts()

        unsaved_hosts = Storage.objects.get_unsaved_hostids()
        hosts = self.storage2.get_hosts().keys()
        self.assertEqual(len(unsaved_hosts), len(hosts), "Missing host number not match.")

        [ h.delete() for h in Host.objects.all()[0:5] ]
        unsaved_hosts = Storage.objects.get_unsaved_hostids()
        self.assertEqual(len(unsaved_hosts), len(hosts)+5, "Missing host number not match.")

    def test_find_host(self):
        self.storage1._update_hosts()
        host = Host.objects.all()[0]

        whereisit = Storage.objects.which_storage(host.hostid)
        self.assertEqual(self.storage1, whereisit, "Host not found on its storage.") 
        host.storage = self.storage2
        host.save()
        whereisit = Storage.objects.which_storage(host.hostid)
        self.assertEqual(self.storage1, whereisit, "Host not found when on bad storage.") 

        host.hostid = 'False test ID'
        host.save()
        whereisit = Storage.objects.which_storage(host.hostid)
        self.assertIsNone(whereisit, "False host found on a storage.") 

    def test_repair_hosts(self):
        # All storage1's hosts are bad
        self.storage1._update_hosts()
        Host.objects.all().update(storage=self.storage2)

        # Get the crap and test it
        bad_hosts = Storage.objects.get_bad_referenced_hostids()
        self.assertEqual(len(bad_hosts), Host.objects.count())

        # Repair and test
        Storage.objects.repair_hosts()
        bad_hosts = Storage.objects.get_bad_referenced_hostids()
        self.assertEqual(len(bad_hosts), 0, "There are always bad referenced %i host(s)." % len(bad_hosts))
