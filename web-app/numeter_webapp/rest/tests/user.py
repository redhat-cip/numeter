"""
Tests for user REST management.
"""

from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase, APIClient, APITestCase
from core.models import User, Group
from core.management.commands.user import Command
from core.tests.utils import set_users
from rest.tests.utils import set_clients

LIST_URL = reverse('user-list')
#DETAIL_URL = reverse('user-detail')

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
