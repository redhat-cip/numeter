"""
Tests for host REST management.
"""

from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase
from core.models import Host
from core.tests.utils import set_users, set_storage
from rest.tests.utils import set_clients

LIST_URL = reverse('host-list')

class Host_GET_list_Test(APILiveServerTestCase):
    """
    Test GET list. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/hosts/ -H 'Accept: application/json'``
    """
    @set_storage(extras=['host'])
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
        """Granted access to simple user with filtered hosts."""
        r = self.user_client.get(LIST_URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)


class Host_GET_detail_Test(APILiveServerTestCase):
    """
    Test GET details. Same as
    ``curl -i -X GET http://127.0.0.1:8081/rest/hosts/1 -H 'Accept: application/json'``
    """
    @set_storage(extras=['host'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('host-detail', args=[self.host.pk])
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
        """Forbidden access to simple user with foreign host."""
        self.DETAIL_URL = reverse('host-detail', args=[Host.objects.exclude(pk=self.host.pk)[0].pk])
        r = self.user_client.get(self.DETAIL_URL)
        self.assertEqual(r.status_code, 404, 'Bad response (%i)' % r.status_code)


class Host_POST_Test(APILiveServerTestCase):
    """
    Test POST. Same as
    ``curl -i -X POST http://127.0.0.1:8081/rest/hosts/ -H 'Accept: application/json'``
    """
    @set_storage(extras=['host'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.hostid = self.host.hostid
        Host.objects.all().delete()

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.post(LIST_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {'hostid': self.hostid}
        r = self.admin_client.post(LIST_URL, data=data)
        self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        r = self.user_client.post(LIST_URL)
        self.assertEqual(r.status_code, 403, 'Bad response (%i)' % r.status_code)


class Host_DELETE_Test(APILiveServerTestCase):
    """
    Test DELETE. Same as
    ``curl -i -X DELETE http://127.0.0.1:8081/rest/hosts/1 -H 'Accept: application/json'``
    """
    @set_storage(extras=['host'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('host-detail', args=[self.host.pk])

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


class Host_PATCH_Test(APILiveServerTestCase):
    """
    Test PATCH. Same as
    ``curl -i -X PATCH http://127.0.0.1:8081/rest/hosts/1 -H 'Accept: application/json'``
    """
    @set_storage(extras=['host'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.DETAIL_URL = reverse('host-detail', args=[self.host.pk])

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.patch(self.DETAIL_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {'name':'NEW HOST'}
        r = self.admin_client.patch(self.DETAIL_URL, data=data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        r = self.user_client.patch(self.DETAIL_URL)
        self.assertEqual(r.status_code, 403, 'Bad response (%i)' % r.status_code)


class Host_POST_create_plugins_Test(APILiveServerTestCase):
    """
    Test POST. Same as
    ``curl -i -X POST http://127.0.0.1:8081/rest/hosts/1/create_plugins/ -H 'Accept: application/json'``
    """
    @set_storage(extras=['host'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.PLUGIN_URL = reverse('host-create-plugins', args=[self.host.pk])
        self.plugins = self.host.get_plugins()
        self.host.group = self.group
        self.host.save()
        self.user.groups.add(self.group.pk)

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.post(self.PLUGIN_URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {'plugins': self.plugins}
        r = self.admin_client.post(self.PLUGIN_URL, data=data)
        self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Forbidden access to simple user."""
        data = {'plugins': self.plugins}
        r = self.user_client.post(self.PLUGIN_URL, data=data)
        self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)

    def test_without_data(self):
        """Create all host's plugin if no one is specified."""
        r = self.admin_client.post(self.PLUGIN_URL)
        self.assertEqual(r.status_code, 201, 'Bad response (%i)' % r.status_code)

