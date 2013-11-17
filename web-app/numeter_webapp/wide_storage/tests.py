"""
Tests for wide_storage.
"""

from django.core.urlresolvers import reverse
from rest_framework.test import APILiveServerTestCase
from core.tests.utils import set_storage, set_users
from rest.tests.utils import set_clients

class Wide_Storage_hosts_Test(APILiveServerTestCase):
    """
    Test GET host list. Same as
    ``curl -i -X GET http://127.0.0.1:8081/wide_storage/hosts -H 'Accept: application/json'``
    """
    @set_storage(extras=['host'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.URL = reverse('wide-storage-hosts')

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.get(self.URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        r = self.admin_client.get(self.URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Granted access to simple user with filtered hosts."""
        r = self.user_client.get(self.URL)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)


class Wide_Storage_hinfo_Test(APILiveServerTestCase):
    """
    Test GET host info. Same as
    ``curl -i -X GET http://127.0.0.1:8081/wide_storage/hinfo -H 'Accept: application/json'``
    """
    @set_storage(extras=['host'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.URL = reverse('wide-storage-hinfo')

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.get(self.URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {'host': self.host.hostid}
        r = self.admin_client.get(self.URL, data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Granted access to simple user with his host."""
        data = {'host': self.host.hostid}
        r = self.admin_client.get(self.URL, data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_foreign_host(self):
        """Forbidden access to simple user with foreign host."""
        data = {'host': self.host.hostid}
        r = self.user_client.get(self.URL, data)
        self.assertEqual(r.status_code, 404, 'Bad response (%i)' % r.status_code)


class Wide_Storage_list_Test(APILiveServerTestCase):
    """
    Test GET host plugin list. Same as
    ``curl -i -X GET http://127.0.0.1:8081/wide_storage/list -H 'Accept: application/json'``
    """
    @set_storage(extras=['host'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.URL = reverse('wide-storage-list')

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.get(self.URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        data = {'host': self.host.hostid}
        r = self.admin_client.get(self.URL, data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Granted access to simple user with his plugin."""
        data = {'host': self.host.hostid}
        r = self.admin_client.get(self.URL, data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_foreign_host(self):
        """Forbidden access to simple user with foreign plugin."""
        data = {'host': self.host.hostid}
        r = self.user_client.get(self.URL, data)
        self.assertEqual(r.status_code, 404, 'Bad response (%i)' % r.status_code)


class Wide_Storage_info_Test(APILiveServerTestCase):
    """
    Test GET source data. Same as
    ``curl -i -X GET http://127.0.0.1:8081/wide_storage/info -H 'Accept: application/json'``
    """
    @set_storage(extras=['host'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.URL = reverse('wide-storage-info')
        plugin = self.host.get_plugin_list()[0]
        self.data = {'host': self.host.hostid, 'plugin':plugin}

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.get(self.URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        r = self.admin_client.get(self.URL, self.data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Granted access to simple user with his plugin."""
        r = self.admin_client.get(self.URL, self.data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_foreign_host(self):
        """Forbidden access to simple user with foreign plugin."""
        r = self.user_client.get(self.URL, self.data)
        self.assertEqual(r.status_code, 404, 'Bad response (%i)' % r.status_code)


class Wide_Storage_data_Test(APILiveServerTestCase):
    """
    Test GET source data. Same as
    ``curl -i -X GET http://127.0.0.1:8081/wide_storage/data -H 'Accept: application/json'``
    """
    @set_storage(extras=['host'])
    @set_users()
    @set_clients()
    def setUp(self):
        self.URL = reverse('wide-storage-data')
        plugin = self.host.get_plugin_list()[0]
        ds = self.host.get_plugin_data_sources(plugin)[0]
        self.data = {'host': self.host.hostid, 'plugin':plugin, 'ds':ds, 'res': 'Daily'}

    def test_anonymous(self):
        """Forbidden access to anonymous."""
        r = self.client.get(self.URL)
        self.assertEqual(r.status_code, 401, 'Bad response (%i)' % r.status_code)

    def test_superuser(self):
        """Granted access for superuser."""
        r = self.admin_client.get(self.URL, self.data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_simple_user(self):
        """Granted access to simple user with his plugin."""
        r = self.admin_client.get(self.URL, self.data)
        self.assertEqual(r.status_code, 200, 'Bad response (%i)' % r.status_code)

    def test_foreign_host(self):
        """Forbidden access to simple user with foreign plugin."""
        r = self.user_client.get(self.URL, self.data)
        self.assertEqual(r.status_code, 404, 'Bad response (%i)' % r.status_code)
