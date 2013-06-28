from django.test import TestCase
from django.conf import settings
from core.models import Storage, Host


class Storage_TestCase(TestCase):
    fixtures = ['test_storage.json']

    def setUp(self):
        if settings.TEST_STORAGE['address']:
            self.storage = Storage.objects.get(pk=1)
        else:
            self.storage = Storage.objects.create(**settings.TEST_STORAGE)

    def test_proxy(self):
        url = 'http://%s:%s/' % (self.storage.address, self.storage.port)
        response = self.storage.proxy.open(url)
        self.assertEqual(reponse, 200, "Bad response code (%i)." % response.code)

    def test_get_hosts(self):
        hosts_dict = self.storage.get_hosts()
        self.assertIsInstance(hosts_dict, list, "Invalide response type, should be list.")

#    def test_create_host_from_storage(self):
#        a = None
#
#    def test_get_info(self):
#        hosts_dict = self.storage.get_info()
#        self.assertIsInstance(hosts_dict, list, "Invalide response type, should be list.")
