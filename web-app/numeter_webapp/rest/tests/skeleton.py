"""
Tests for skeleton REST management.
"""

from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from multiviews.models import Skeleton
from core.tests.utils import set_users, set_storage
from multiviews.tests.utils import set_views, set_multiviews
from rest.tests.utils import set_clients

LIST_URL = reverse('skeleton-list')

class Skeleton_GET_list_Test(APITestCase):
    """
    Test GET list. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/skeletons/ -H 'Accept: application/json'``
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
        """Granted access to simple user."""
        r = self.user_client.get(LIST_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)


class Skeleton_GET_detail_Test(APITestCase):
    """
    Test GET details. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/skeletons/1 -H 'Accept: application/json'``
    """
    @set_users()
    @set_clients()
    def setUp(self):
        self.skeleton = Skeleton.objects.all()[0]
        self.DETAIL_URL = reverse('skeleton-detail', args=[self.skeleton.id])

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
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)


class Skeleton_POST_Test(APITestCase):
    """
    Test POST. Same as
    ``curl -i -X POST http://127.0.0.1:8081/skeleton/views/ -H 'Accept: application/json'``
    """
    @set_users()
    @set_clients()
    def setUp(self):
        self.data = {
            'name':'NEW SKELETON',
            'plugin_pattern': '.*',
            'source_pattern': '.*',
        }

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.post(LIST_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        r = self.admin_client.post(LIST_URL, data=self.data)
        self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        r = self.user_client.post(LIST_URL, self.data)
        self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)


class Skeleton_DELETE_Test(APITestCase):
    """
    Test DELETE. Same as
    ``curl -i -X DELETE http://127.0.0.1:8081/rest/skeletons/1 -H 'Accept: application/json'``
    """
    @set_users()
    @set_clients()
    def setUp(self):
        self.skeleton = Skeleton.objects.all()[0]
        self.DETAIL_URL = reverse('skeleton-detail', args=[self.skeleton.id])

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
        self.assertEqual(r.status_code, 204, 'Bad response (%i)' % r.status_code)


class Skeleton_PATCH_Test(APITestCase):
    """
    Test PATCH. Same as
    ``curl -i -X PATCH http://127.0.0.1:8081/rest/skeletons/1 -H 'Accept: application/json'``
    """
    @set_users()
    @set_clients()
    def setUp(self):
        self.skeleton = Skeleton.objects.all()[0]
        self.DETAIL_URL = reverse('skeleton-detail', args=[self.skeleton.id])
        self.data = {'name':'NEW SKELETON'}

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.patch(self.DETAIL_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        r = self.admin_client.patch(self.DETAIL_URL, data=self.data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        r = self.user_client.patch(self.DETAIL_URL, data=self.data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)


class Skeleton_DELETE_list_Test(APITestCase):
    """
    Test DELETE list. Same as
    ``curl -i -X DELETE http://127.0.0.1:8081/rest/skeleton/ -H 'Accept: application/json'``
    """
    @set_users()
    @set_clients()
    def setUp(self):
        self.skeleton = Skeleton.objects.all()[0]

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.delete(LIST_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {'id': [self.skeleton.id]}
        r = self.admin_client.delete(LIST_URL, data=data)
        self.assertEqual(r.status_code, 204, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        data = {'id': [self.skeleton.id]}
        r = self.user_client.delete(LIST_URL, data=data)
        self.assertEqual(r.status_code, 204, 'Bad response (%i)' % r.status_code)
