"""
Tests for multiview REST management.
"""

from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from multiviews.models import Multiview
from core.tests.utils import set_users, set_storage
from multiviews.tests.utils import set_views, set_multiviews
from rest.tests.utils import set_clients

LIST_URL = reverse('multiview-list')

class Multiview_GET_list_Test(APITestCase):
    """
    Test GET list. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/multiviews/ -H 'Accept: application/json'``
    """
    @set_storage(extras=['host', 'plugin', 'source'])
    @set_users()
    @set_clients()
    @set_views()
    @set_multiviews()
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


class Multiview_GET_detail_Test(APITestCase):
    """
    Test GET details. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/multiviews/1 -H 'Accept: application/json'``
    """
    @set_storage(extras=['host', 'plugin', 'source'])
    @set_users()
    @set_clients()
    @set_views()
    @set_multiviews()
    def setUp(self):
        self.DETAIL_URL = reverse('multiview-detail', args=[self.multiview_not_owned.id])

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
        self.assertEqual(r.status_code, 404, 'Bad response (%i)' % r.status_code)

    def test_simple_user_with_his_multiview(self):
        """Granted access to simple user with his multiview."""
        self.DETAIL_URL = reverse('multiview-detail', args=[self.multiview_user.id])
        r = self.user_client.get(self.DETAIL_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user_with_his_group_multiview(self):
        """Granted access to simple user with his group's multiview."""
        self.DETAIL_URL = reverse('multiview-detail', args=[self.multiview_group.id])
        r = self.user_client.get(self.DETAIL_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)


# class View_POST_Test(APITestCase):
#     """
#     Test POST. Same as
#     ``curl -i -X POST http://127.0.0.1:8081/rest/views/ -H 'Accept: application/json'``
#     """
#     @set_storage(extras=['host', 'plugin', 'source'])
#     @set_users()
#     @set_clients()
#     @set_views()
#     def setUp(self):
#         pass
# 
#     def test_anonymous(self):
#         """Forbidden access to anonymous."""
#         r = self.client.post(LIST_URL)
#         self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)
# 
#     def test_superuser(self):
#         """Granted access for superuser."""
#         data = {
#             'name':'NEW VIEW',
#             'address': 'localhost',
#         }
#         r = self.admin_client.post(LIST_URL, data=data)
#         self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)
# 
#     def test_simple_user(self):
#         """Forbidden access to simple user."""
#         r = self.user_client.post(LIST_URL)
#         self.assertEqual(r.status_code, 403, 'Bad response (%i)' % r.status_code)


class Multiview_DELETE_Test(APITestCase):
    """
    Test DELETE. Same as
    ``curl -i -X DELETE http://127.0.0.1:8081/rest/multiviews/1 -H 'Accept: application/json'``
    """
    @set_storage(extras=['host', 'plugin', 'source'])
    @set_users()
    @set_clients()
    @set_views()
    @set_multiviews()
    def setUp(self):
        self.DETAIL_URL = reverse('multiview-detail', args=[self.multiview_not_owned.id])

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

    def test_simple_user_with_his_multiview(self):
        """Granted access to simple user with his multiview."""
        self.DETAIL_URL = reverse('multiview-detail', args=[self.multiview_user.id])
        r = self.user_client.get(self.DETAIL_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user_with_his_group_multiview(self):
        """Granted access to simple user with his group's multiview."""
        self.DETAIL_URL = reverse('multiview-detail', args=[self.multiview_group.id])
        r = self.user_client.get(self.DETAIL_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)


class Multiview_DELETE_list_Test(APITestCase):
    """
    Test DELETE list. Same as
    ``curl -i -X DELETE http://127.0.0.1:8081/rest/multiviews/ -H 'Accept: application/json'``
    """
    @set_storage(extras=['host', 'plugin', 'source'])
    @set_users()
    @set_clients()
    @set_views()
    @set_multiviews()
    def setUp(self):
        pass

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.delete(LIST_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {'id': [self.multiview_user.id]}
        r = self.admin_client.delete(LIST_URL, data=data)
        self.assertEqual(r.status_code, 204, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        data = {'id': [self.multiview_user.id]}
        r = self.user_client.delete(LIST_URL, data=data)
        self.assertEqual(r.status_code, 204, 'Bad response (%i)' % r.status_code)

# class Storage_PATCH_Test(APITestCase):
#     """
#     Test PATCH. Same as
#     ``curl -i -X PATCH http://127.0.0.1:8081/rest/storages/1 -H 'Accept: application/json'``
#     """
#     @set_storage()
#     @set_users()
#     @set_clients()
#     def setUp(self):
#         self.DETAIL_URL = reverse('storage-detail', args=[self.storage.pk])
# 
#     def test_anonymous(self):
#         """Forbidden access to anonymous."""
#         data = {'name':'NEW GROUP'}
#         r = self.client.patch(self.DETAIL_URL, data=data)
#         self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)
# 
#     def test_superuser(self):
#         """Granted access for superuser."""
#         data = {'name':'NEW GROUP'}
#         r = self.admin_client.patch(self.DETAIL_URL, data=data)
#         self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)
# 
#     def test_simple_user(self):
#         """Forbidden access to simple user."""
#         data = {'name':'NEW STORAGE'}
#         r = self.user_client.patch(self.DETAIL_URL, data=data)
#         self.assertEqual(r.status_code, 403, 'Bad response (%i)' % r.status_code)
