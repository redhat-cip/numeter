from tastypie.test import ResourceTestCase
from core.tests.utils import set_storage, set_users
from core.models import Data_Source as Source


class Source_Test(ResourceTestCase):
    """
    Tests for source management API.
    """
    @set_users()
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        super(Source_Test, self).setUp()
        self.source = Source.objects.all()[0]

    def get_credentials(self):
        return self.create_basic('root', 'toto')

    def test_get_list(self):
        """Get list of sources."""
        url = '/api/source/'
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertValidJSONResponse(r)

    def test_get_detail(self):
        """Get source's detail."""
        url = '/api/source/%i/' % self.source.pk
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertValidJSONResponse(r)

    def test_post(self):
        """Create a source."""
        url = '/api/source/'
        data = {
          'name': 'new source',
          'plugin': 1,
        }
        r = self.api_client.post(url, data=data, authentication=self.get_credentials())
        self.assertHttpCreated(r)
        self.assertTrue(Source.objects.filter(name='new source').exists(), "Source hasn't been created")

    def test_patch(self):
        """Update a source."""
        url = '/api/source/%i/' % self.source.pk
        data = { 'comment': 'roott' }
        r = self.api_client.patch(url, data=data, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertEqual(Source.objects.get(pk=self.source.pk).name, 'comment', "Data are unchanged.")

    def test_delete(self):
        """Delete a source."""
        url = '/api/source/%i/' % self.source.pk
        r = self.api_client.delete(url, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertFalse(Source.objects.filter(pk=self.source.pk).exists(), "Source hasn't been deleted.")

    def test_delete_list(self):
        """Delete a source list."""
        url = '/api/source/'
        data = {
          'deleted_objects': [
            '/api/source/%i/' % self.source.pk,
          ],
          'objects':[],
        }
        r = self.api_client.patch(url, data=data, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertFalse(Source.objects.filter(pk=self.source.pk).exists(), "Source hasn't been deleted.")


class Source_Forbidden_Test(ResourceTestCase):
    """
    Tests for unauthorized access.
    """
    @set_users()
    def setUp(self):
        super(Source_Forbidden_Test, self).setUp()

    def get_credentials(self):
        return self.create_basic('Client', 'toto')

    def test_anonymous(self):
        """Ban anonymous."""
        url = '/api/source/'
        r = self.api_client.get(url)
        self.assertHttpUnauthorized(r)

    def test_simple_user(self):
        """Ban non admin."""
        url = '/api/source/'
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertHttpForbidden(r)
