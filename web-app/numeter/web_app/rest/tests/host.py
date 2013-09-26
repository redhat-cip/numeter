from tastypie.test import ResourceTestCase
from core.tests.utils import set_storage, set_users
from core.models import Host


class Host_Test(ResourceTestCase):
    """
    Tests for host management API.
    """
    @set_users()
    @set_storage(extras=['host'])
    def setUp(self):
        super(Host_Test, self).setUp()
        self.host = Host.objects.all()[0]

    def get_credentials(self):
        return self.create_basic('root', 'toto')

    def test_get_list(self):
        """Get list of hosts."""
        url = '/api/host/'
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertValidJSONResponse(r)

    def test_get_detail(self):
        """Get host's detail."""
        url = '/api/host/%i/' % self.host.pk
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertValidJSONResponse(r)

    def test_post(self):
        """Create a host."""
        url = '/api/host/'
        data = {
          'name': 'new host',
          'storage': 1,
        }
        r = self.api_client.post(url, data=data, authentication=self.get_credentials())
        self.assertHttpCreated(r)
        self.assertTrue(Host.objects.filter(name='new host').exists(), "Host hasn't been created")

    def test_patch(self):
        """Update a host."""
        url = '/api/host/%i/' % self.host.pk
        data = { 'name': 'roott' }
        r = self.api_client.patch(url, data=data, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertEqual(Host.objects.get(pk=1).name, 'roott', "Data are unchanged.")

    def test_delete(self):
        """Delete a host."""
        url = '/api/host/%i/' % self.host.pk
        r = self.api_client.delete(url, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertFalse(Host.objects.filter(pk=self.host.pk).exists(), "Host hasn't been deleted.")

    def test_delete_list(self):
        """Delete a host list."""
        url = '/api/host/'
        data = {
          'deleted_objects': [
            '/api/host/%i/' % self.host.pk,
          ],
          'objects':[],
        }
        r = self.api_client.patch(url, data=data, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertFalse(Host.objects.filter(pk=self.host.pk).exists(), "Host hasn't been deleted.")


class Host_Forbidden_Test(ResourceTestCase):
    """
    Tests for unauthorized access.
    """
    @set_users()
    def setUp(self):
        super(Host_Forbidden_Test, self).setUp()

    def get_credentials(self):
        return self.create_basic('host', 'toto')

    def test_anonymous(self):
        """Ban anonymous."""
        url = '/api/host/'
        r = self.api_client.get(url)
        self.assertHttpUnauthorized(r)

    def test_simple_user(self):
        """Ban non host."""
        url = '/api/host/'
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertHttpForbidden(r)

