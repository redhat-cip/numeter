"""
Tests for user REST management.
"""

from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from core.models import User
from core.tests.utils import set_users
from rest.tests.utils import set_clients

LIST_URL = reverse('user-list')
LOGIN_URL = '/auth/login/'
LOGOUT_URL = '/auth/logout/'

class User_GET_list_Test(APITestCase):
    """
    Test GET list. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/users/ -H 'Accept: application/json'``
    """
    @set_users()
    @set_clients()
    def setUp(self):
        pass

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.get(LIST_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        r = self.admin_client.get(LIST_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        r = self.user_client.get(LIST_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)


class User_GET_detail_Test(APITestCase):
    """
    Test GET details. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/users/1 -H 'Accept: application/json'``
    """
    @set_users()
    @set_clients()
    def setUp(self):
        pass

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        DETAIL_URL = reverse('user-detail', args=[self.user.pk])
        r = self.client.get(DETAIL_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        DETAIL_URL = reverse('user-detail', args=[self.user.pk])
        r = self.admin_client.get(DETAIL_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        DETAIL_URL = reverse('user-detail', args=[self.user2.pk])
        r = self.user_client.get(DETAIL_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_user_himself(self):
        """Granted access to user himself."""
        DETAIL_URL = reverse('user-detail', args=[self.user.pk])
        r = self.user_client.get(DETAIL_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)


class User_POST_Test(APITestCase):
    """
    Test POST. Same as
    ``curl -i -X POST http://127.0.0.1:8081/rest/users/ -H 'Accept: application/json'``
    """
    @set_users()
    @set_clients()
    def setUp(self):
        pass

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        data = {'username':'NEW USER'}
        r = self.client.post(LIST_URL, data=data)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {'username':'NEW USER'}
        r = self.admin_client.post(LIST_URL, data=data)
        self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        data = {'username':'NEW USER'}
        r = self.user_client.post(LIST_URL, data=data)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)


class User_DELETE_Test(APITestCase):
    """
    Test DELETE. Same as
    ``curl -i -X DELETE http://127.0.0.1:8081/rest/users/1 -H 'Accept: application/json'``
    """
    @set_users()
    @set_clients()
    def setUp(self):
        pass

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        DETAIL_URL = reverse('user-detail', args=[self.user.pk])
        r = self.client.delete(DETAIL_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        DETAIL_URL = reverse('user-detail', args=[self.user.pk])
        r = self.admin_client.delete(DETAIL_URL)
        self.assertEqual(r.status_code, 204, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        DETAIL_URL = reverse('user-detail', args=[self.user.pk])
        r = self.user_client.delete(DETAIL_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)


class User_PATCH_Test(APITestCase):
    """
    Test PATCH. Same as
    ``curl -i -X PATCH http://127.0.0.1:8081/rest/users/1 -H 'Accept: application/json'``
    """
    @set_users()
    @set_clients()
    def setUp(self):
        pass

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        DETAIL_URL = reverse('user-detail', args=[self.user.pk])
        data = {'groups':[1,2]}
        r = self.client.patch(DETAIL_URL, data=data)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        DETAIL_URL = reverse('user-detail', args=[self.user.pk])
        data = {'groups':[1,2]}
        r = self.admin_client.patch(DETAIL_URL, data=data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        DETAIL_URL = reverse('user-detail', args=[self.user2.pk])
        data = {'groups':[1,2]}
        r = self.user_client.patch(DETAIL_URL, data=data)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)


class User_POST_set_password_Test(APITestCase):
    """
    Test POST. Same as
    ``curl -i -X POST http://127.0.0.1:8081/rest/users/1/set_password -H 'Accept: application/json'``
    """
    @set_users()
    @set_clients()
    def setUp(self):
        pass

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        PASSWORD_URL = reverse('user-set-password', args=[self.user.pk])
        data = {'password':'test'}
        r = self.client.post(PASSWORD_URL, data=data)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        PASSWORD_URL = reverse('user-set-password', args=[self.user.pk])
        data = {'password':'test'}
        r = self.admin_client.post(PASSWORD_URL, data=data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)
        # Test user to log with new pass
        self.client.post(LOGIN_URL, {'username':self.user.username, 'password':'test'})
        DETAIL_URL = reverse('user-detail', args=[self.user.pk])
        r = self.user_client.get(DETAIL_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        PASSWORD_URL = reverse('user-set-password', args=[self.user2.pk])
        data = {'password':'test'}
        r = self.user_client.post(PASSWORD_URL, data=data)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_user_himself(self):
        """Granted access to user himself."""
        PASSWORD_URL = reverse('user-set-password', args=[self.user.pk])
        data = {'password':'test'}
        r = self.user_client.post(PASSWORD_URL, data=data)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)
