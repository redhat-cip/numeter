from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from core.tests.utils import set_users


class Index_Test(TestCase):
    @set_users()
    def setUp(self):
        self.c = Client()
        self.c.login(username='root', password='toto')

    def test_index(self):
        """Get index."""
        url = reverse('index')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)

    def test_apropos(self):
        """Get apropos."""
        url = reverse('apropos')
        r = self.c.get(url)
        self.assertEqual(r.status_code, 200, "Bad response code (%i)." % r.status_code)
