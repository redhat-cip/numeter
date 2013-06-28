from django.test import TestCase
from core.models import Storage, Host


# TODO : Make dynamic test Storage
class Storage_TestCase(TestCase):
    fixtures = ['test_storage.json']

    def setUp(self):
        self.storage = Storage.objects.get(pk=1)

    def test_proxy(self):
        response = self.storage.proxy.open('http://%s:%s/' % (self.address,self.port))
        self.assertEqual(reponse, 200, "Bad response code (%i)." % response.code)

    def test_get_hosts(self):
        hosts_dict = self.storage.get_hosts()
        self.assertIsInstance(hosts_dict, list, "Invalide response type, should be list.")
