"""
Tests for source REST management.
"""

from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase, APITestCase
from core.models import Data_Source as Source
from core.tests.utils import set_users, set_storage
from rest.tests.utils import set_clients

LIST_URL = reverse('data_source-list')

class Source_GET_list_Test(APILiveServerTestCase):
    """
    Test GET list. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/sources/ -H 'Accept: application/json'``
    """
    @set_storage(extras=['host','plugin','source'])
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
        """Granted access to simple user with filtered sources."""
        r = self.user_client.get(LIST_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)


class Source_GET_detail_Test(APILiveServerTestCase):
    """
    Test GET details. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/sources/1 -H 'Accept: application/json'``
    """
    @set_storage(extras=['host', 'plugin', 'source'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('data_source-detail', args=[self.source.pk])
        self.host.group = self.group
        self.host.save()
        self.user.groups.add(self.group.pk)

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.get(self.DETAIL_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        r = self.admin_client.get(self.DETAIL_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Granted access to simple user with his own."""
        r = self.user_client.get(self.DETAIL_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_foreign_host(self):
        """Forbidden access to simple user with foreign source."""
        self.DETAIL_URL = reverse('data_source-detail', args=[Source.objects.exclude(pk=self.source.pk)[0].pk])
        r = self.user_client.get(self.DETAIL_URL)
        self.assertEqual(r.status_code, 404, 'Bad response (%i)' % r.status_code)


class Source_POST_Test(APITestCase):
    """
    Test POST. Same as
    ``curl -i -X POST http://127.0.0.1:8081/rest/sources/ -H 'Accept: application/json'``
    """
    @set_users()
    @set_clients()
    def setUp(self):
        pass

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.post(LIST_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        r = self.admin_client.post(LIST_URL)
        self.assertEqual(r.status_code, 403, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        r = self.user_client.post(LIST_URL)
        self.assertEqual(r.status_code, 403, 'Bad response (%i)' % r.status_code)


class Source_DELETE_Test(APILiveServerTestCase):
    """
    Test DELETE. Same as
    ``curl -i -X DELETE http://127.0.0.1:8081/rest/sources/1 -H 'Accept: application/json'``
    """
    @set_storage(extras=['host', 'plugin', 'source'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('data_source-detail', args=[self.host.pk])

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
        self.assertEqual(r.status_code, 404, 'Bad response (%i)' % r.status_code)


class Source_PATCH_Test(APILiveServerTestCase):
    """
    Test PATCH. Same as
    ``curl -i -X PATCH http://127.0.0.1:8081/rest/sources/1 -H 'Accept: application/json'``
    """
    @set_storage(extras=['host', 'plugin', 'source'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('data_source-detail', args=[self.source.pk])

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.patch(self.DETAIL_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {'name':'NEW PLUGIN'}
        r = self.admin_client.patch(self.DETAIL_URL, data=data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Granted access to simple user."""
        r = self.user_client.patch(self.DETAIL_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user_with_foreign_source(self):
        """Forbidden access to simple user."""
        self.source = Source.objects.exclude(plugin__host__group=self.group)[0]
        self.DETAIL_URL = self.source.get_rest_detail_url()
        r = self.user_client.patch(self.DETAIL_URL)
        self.assertEqual(r.status_code, 404, 'Bad response (%i)' % r.status_code)


class Source_DELETE_list_Test(APILiveServerTestCase):
    """
    Test DELETE list. Same as
    ``curl -i -X DELETE http://127.0.0.1:8081/rest/sources/ -H 'Accept: application/json'``
    """
    @set_storage(extras=['host', 'plugin', 'source'])
    @set_users()
    @set_clients()
    def setUp(self):
        pass

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.delete(LIST_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {'id': [self.source.id]}
        r = self.admin_client.delete(LIST_URL, data=data)
        self.assertEqual(r.status_code, 204, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        data = {'id': [self.source.id]}
        r = self.user_client.delete(LIST_URL, data=data)
        self.assertEqual(r.status_code, 404, 'Bad response (%i)' % r.status_code)
