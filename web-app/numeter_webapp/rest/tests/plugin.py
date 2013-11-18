"""
Tests for plugin REST management.
"""

from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase, APITestCase
from core.models import Plugin
from core.tests.utils import set_users, set_storage
from rest.tests.utils import set_clients

LIST_URL = reverse('plugin-list')

class Plugin_GET_list_Test(APILiveServerTestCase):
    """
    Test GET list. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/plugins/ -H 'Accept: application/json'``
    """
    @set_storage(extras=['host','plugin'])
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
        """Granted access to simple user with filtered plugins."""
        r = self.user_client.get(LIST_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)


class Plugin_GET_detail_Test(APILiveServerTestCase):
    """
    Test GET details. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/plugins/1 -H 'Accept: application/json'``
    """
    @set_storage(extras=['host', 'plugin'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('plugin-detail', args=[self.plugin.pk])
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
        """Forbidden access to simple user with foreign plugin."""
        self.DETAIL_URL = reverse('plugin-detail', args=[Plugin.objects.exclude(pk=self.plugin.pk)[0].pk])
        r = self.user_client.get(self.DETAIL_URL)
        self.assertEqual(r.status_code, 404, 'Bad response (%i)' % r.status_code)


class Plugin_POST_Test(APITestCase):
    """
    Test POST. Same as
    ``curl -i -X POST http://127.0.0.1:8081/rest/plugins/ -H 'Accept: application/json'``
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


class Plugin_DELETE_Test(APILiveServerTestCase):
    """
    Test DELETE. Same as
    ``curl -i -X DELETE http://127.0.0.1:8081/rest/plugins/1 -H 'Accept: application/json'``
    """
    @set_storage(extras=['host', 'plugin'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('plugin-detail', args=[self.host.pk])

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


class Plugin_PATCH_Test(APILiveServerTestCase):
    """
    Test PATCH. Same as
    ``curl -i -X PATCH http://127.0.0.1:8081/rest/plugins/1 -H 'Accept: application/json'``
    """
    @set_storage(extras=['host', 'plugin'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('plugin-detail', args=[self.plugin.pk])

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

    def test_simple_user_with_foreign_plugin(self):
        """Forbidden access to simple user with a foreign plugin."""
        self.plugin = Plugin.objects.exclude(host__group=self.group)[0]
        self.DETAIL_URL = self.plugin.get_rest_detail_url()
        r = self.user_client.patch(self.DETAIL_URL)
        self.assertEqual(r.status_code, 404, 'Bad response (%i)' % r.status_code)


class Plugin_POST_create_sources_Test(APILiveServerTestCase):
    """
    Test POST. Same as
    ``curl -i -X POST http://127.0.0.1:8081/rest/plugins/1/create_sources/ -H 'Accept: application/json'``
    """
    @set_storage(extras=['host', 'plugin'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.SOURCE_URL = reverse('plugin-create-sources', args=[self.plugin.pk])
        self.sources = self.plugin.get_data_sources()
        self.host.group = self.group
        self.host.save()
        self.user.groups.add(self.group.pk)

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.post(self.SOURCE_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {'sources': self.sources}
        r = self.admin_client.post(self.SOURCE_URL, data=data)
        self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        data = {'sources': self.sources}
        r = self.user_client.post(self.SOURCE_URL, data=data)
        self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)

    def test_without_data(self):
        """Create all plugin's sources if no one is specified."""
        r = self.admin_client.post(self.SOURCE_URL)
        self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)
