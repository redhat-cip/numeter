from django.core.urlresolvers import reverse
from rest_framework.test import APIClient, APITestCase
from core.models import User
from core.tests.utils import set_users

API_ROOT = reverse('api-root')
LOGIN_URL = '/auth/login/'
LOGOUT_URL = '/auth/logout/'


class Login_Test(APITestCase):
    @set_users()
    def setUp(self):
        self.client = APIClient()

    def test_forbidden_access(self):
        """GET api without logged in."""
        r= self.client.get(API_ROOT)
        self.assertEqual(r.status_code, 401, "Bad response code (%i)." % r.status_code)

    def test_login(self):
        """Log in."""
        r = self.client.post(LOGIN_URL, {'username':'root', 'password':'toto'})
        r = self.client.get(API_ROOT)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_logout(self):
        """Log out."""
        self.client.post(LOGIN_URL, {'username':'root', 'password':'toto'})
        self.client.post(API_ROOT, {'username':'root', 'password':'toto'})
        r = self.client.post(LOGOUT_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

        r= self.client.get(API_ROOT)
        self.assertEqual(r.status_code, 401, "Bad response code (%i)." % r.status_code)
