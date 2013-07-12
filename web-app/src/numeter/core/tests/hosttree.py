from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings

from core.models import User, Storage, Host
from core.tests.utils import storage_enabled


class Hosttree_TestCase(TestCase):
    fixtures = ['test_users.json','test_groups.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')
        if settings.TEST_STORAGE['address']:
            self.storage = Storage.objects.create(**settings.TEST_STORAGE)
            if not self.storage.is_on():
                self.skipTest("Configured storage unreachable.")
            self.storage._update_hosts()
        else:
            self.skipTest("No test storage has been configurated.")

    @storage_enabled()
    def test_group(self):
        url = reverse('hosttree group', args=[''])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    @storage_enabled()
    def test_host(self):
        url = reverse('hosttree host', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    @storage_enabled()
    def test_category(self):
        H = Host.objects.get(pk=1)
        category = H.get_categories()[0]

        url = reverse('hosttree category', args=[1])
        GET = {'category':category}
        r = self.c.get(url, GET)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
