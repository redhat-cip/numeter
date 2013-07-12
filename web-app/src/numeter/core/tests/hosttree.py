from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from core.models import User, Storage, Host


class Hosttree_TestCase(TestCase):
    fixtures = ['test_users.json','test_groups.json','test_storage.json']

    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')
        Storage.objects.get(pk=1)._update_hosts()

    def test_group(self):
        url = reverse('hosttree group', args=[''])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_host(self):
        url = reverse('hosttree host', args=[1])
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_category(self):
        H = Host.objects.get(pk=1)
        category = H.get_categories()[0]

        url = reverse('hosttree category', args=[1])
        GET = {'category':category}
        r = self.c.get(url, GET)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
