from tastypie.test import ResourceTestCase
from core.tests.utils import set_storage, set_users
from core.models import Storage


class Storage_Test(ResourceTestCase):
    """
    Tests for storage management API.
    Only available for admins.
    """
    @set_users()
    @set_storage()
    def setUp(self):
        super(Storage_Test, self).setUp()
        self.storage = Storage.objects.all()[0]

    def get_credentials(self):
        return self.create_basic('root', 'toto')

    def test_get_list(self):
        """Get list of storages."""
        url = '/api/storage/'
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertValidJSONResponse(r)

    def test_get_detail(self):
        """Get storage's detail."""
        url = '/api/storage/%i/' % self.storage.pk
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertValidJSONResponse(r)

    def test_post(self):
        """Create a storage."""
        url = '/api/storage/'
        data = {
          'name': 'new storage',
          'address': 'localhost',
        }
        r = self.api_client.post(url, data=data, authentication=self.get_credentials())
        self.assertHttpCreated(r)
        self.assertTrue(Storage.objects.filter(name='new storage').exists(), "Storage hasn't been created")

    def test_patch(self):
        """Update a storage."""
        url = '/api/storage/%i/' % self.storage.pk
        data = { 'name': 'roott' }
        r = self.api_client.patch(url, data=data, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertEqual(Storage.objects.get(pk=1).name, 'roott', "Data are unchanged.")

    def test_delete(self):
        """Delete a storage."""
        url = '/api/storage/%i/' % self.storage.pk
        r = self.api_client.delete(url, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertFalse(Storage.objects.filter(pk=self.storage.pk).exists(), "Storage hasn't been deleted.")

    def test_delete_list(self):
        """Delete a storage list."""
        url = '/api/storage/'
        data = {
          'deleted_objects': [
            '/api/storage/%i/' % self.storage.pk,
          ],
          'objects':[],
        }
        r = self.api_client.patch(url, data=data, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertFalse(Storage.objects.filter(pk=self.storage.pk).exists(), "Storage hasn't been deleted.")


class Storage_Forbidden_Test(ResourceTestCase):
    """
    Tests for unauthorized access.
    """
    @set_users()
    def setUp(self):
        super(Storage_Forbidden_Test, self).setUp()

    def get_credentials(self):
        return self.create_basic('storage', 'toto')

    def test_anonymous(self):
        """Ban anonymous."""
        url = '/api/storage/'
        r = self.api_client.get(url)
        self.assertHttpUnauthorized(r)

    def test_simple_user(self):
        """Ban non admin."""
        url = '/api/storage/'
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertHttpForbidden(r)

