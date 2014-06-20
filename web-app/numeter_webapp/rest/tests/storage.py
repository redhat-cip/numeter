"""
Tests for storage REST management.
"""

from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase, APILiveServerTestCase
from core.models import Storage
from core.tests.utils import set_users, set_storage
from rest.tests.utils import set_clients

LIST_URL = reverse('storage-list')

class Storage_GET_list_Test(APITestCase):
    """
    Test GET list. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/storages/ -H 'Accept: application/json'``
    """
    @set_storage()
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('storage-detail', args=[self.storage.pk])

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
        self.assertEqual(r.status_code, 403, 'Bad response (%i)' % r.status_code)


class Storage_GET_detail_Test(APITestCase):
    """
    Test GET details. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/storages/1 -H 'Accept: application/json'``
    """
    @set_storage()
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('storage-detail', args=[self.storage.pk])

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.get(self.DETAIL_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        r = self.admin_client.get(self.DETAIL_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        r = self.user_client.get(self.DETAIL_URL)
        self.assertEqual(r.status_code, 403, 'Bad response (%i)' % r.status_code)


class Storage_POST_Test(APITestCase):
    """
    Test POST. Same as
    ``curl -i -X POST http://127.0.0.1:8081/rest/storages/ -H 'Accept: application/json'``
    """
    @set_storage()
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('storage-detail', args=[self.storage.pk])

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.post(LIST_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {
            'name':'NEW STORAGE',
            'address': 'localhost',
        }
        r = self.admin_client.post(LIST_URL, data=data)
        self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        r = self.user_client.post(LIST_URL)
        self.assertEqual(r.status_code, 403, 'Bad response (%i)' % r.status_code)


class Storage_DELETE_Test(APITestCase):
    """
    Test DELETE. Same as
    ``curl -i -X DELETE http://127.0.0.1:8081/rest/storages/1 -H 'Accept: application/json'``
    """
    @set_storage()
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('storage-detail', args=[self.storage.pk])

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.delete(self.DETAIL_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        r = self.admin_client.delete(self.DETAIL_URL)
        self.assertEqual(r.status_code, 204, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        r = self.user_client.delete(self.DETAIL_URL)
        self.assertEqual(r.status_code, 403, 'Bad response (%i)' % r.status_code)


class Storage_PATCH_Test(APITestCase):
    """
    Test PATCH. Same as
    ``curl -i -X PATCH http://127.0.0.1:8081/rest/storages/1 -H 'Accept: application/json'``
    """
    @set_storage()
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('storage-detail', args=[self.storage.pk])

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        data = {'name':'NEW GROUP'}
        r = self.client.patch(self.DETAIL_URL, data=data)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {'name':'NEW GROUP'}
        r = self.admin_client.patch(self.DETAIL_URL, data=data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        data = {'name':'NEW STORAGE'}
        r = self.user_client.patch(self.DETAIL_URL, data=data)
        self.assertEqual(r.status_code, 403, 'Bad response (%i)' % r.status_code)


class Storage_POST_create_hosts_Test(APILiveServerTestCase):
    """
    Test POST. Same as
    ``curl -i -X POST http://127.0.0.1:8081/rest/storages/1/create_hosts/ -H 'Accept: application/json'``
    """
    @set_storage()
    @set_users()
    @set_clients()
    def setUp(self):
        self.STORAGE_URL = reverse('storage-create-hosts', args=[self.storage.id])
        self.hosts = self.storage.get_hosts()

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.post(self.STORAGE_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {'hosts': self.hosts}
        r = self.admin_client.post(self.STORAGE_URL, data=data)
        self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        r = self.user_client.post(self.STORAGE_URL)
        self.assertEqual(r.status_code, 403, 'Bad response (%i)' % r.status_code)

    def test_without_data(self):
        """Create all hosts's sources if no one is specified."""
        r = self.admin_client.post(self.STORAGE_URL)
        self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)
