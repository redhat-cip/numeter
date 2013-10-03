from tastypie.test import ResourceTestCase
from core.tests.utils import set_storage, set_users
from core.models import Plugin


class Plugin_Test(ResourceTestCase):
    """
    Tests for plugin management API.
    """
    @set_users()
    @set_storage(extras=['host','plugin'])
    def setUp(self):
        super(Plugin_Test, self).setUp()
        self.plugin = Plugin.objects.all()[0]

    def get_credentials(self):
        return self.create_basic('root', 'toto')

    def test_get_list(self):
        """Get list of plugins."""
        url = '/api/plugin/'
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertValidJSONResponse(r)

    def test_get_detail(self):
        """Get plugin's detail."""
        url = '/api/plugin/%i/' % self.plugin.pk
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertValidJSONResponse(r)

    def test_post(self):
        """Create a plugin."""
        url = '/api/plugin/'
        data = {
          'name': 'new plugin',
          'host': 1,
        }
        r = self.api_client.post(url, data=data, authentication=self.get_credentials())
        self.assertHttpCreated(r)
        self.assertTrue(Plugin.objects.filter(name='new plugin').exists(), "Plugin hasn't been created")

    def test_patch(self):
        """Update a plugin."""
        url = '/api/plugin/%i/' % self.plugin.pk
        data = { 'comment': 'roott' }
        r = self.api_client.patch(url, data=data, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertEqual(Plugin.objects.get(pk=self.plugin.pk).name, 'comment', "Data are unchanged.")

    def test_delete(self):
        """Delete a plugin."""
        url = '/api/plugin/%i/' % self.plugin.pk
        r = self.api_client.delete(url, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertFalse(Plugin.objects.filter(pk=self.plugin.pk).exists(), "Plugin hasn't been deleted.")

    def test_delete_list(self):
        """Delete a plugin list."""
        url = '/api/plugin/'
        data = {
          'deleted_objects': [
            '/api/plugin/%i/' % self.plugin.pk,
          ],
          'objects':[],
        }
        r = self.api_client.patch(url, data=data, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertFalse(Plugin.objects.filter(pk=self.plugin.pk).exists(), "Plugin hasn't been deleted.")


class Plugin_Forbidden_Test(ResourceTestCase):
    """
    Tests for unauthorized access.
    """
    @set_users()
    def setUp(self):
        super(Plugin_Forbidden_Test, self).setUp()

    def get_credentials(self):
        return self.create_basic('Client', 'toto')

    def test_anonymous(self):
        """Ban anonymous."""
        url = '/api/plugin/'
        r = self.api_client.get(url)
        self.assertHttpUnauthorized(r)

    def test_simple_user(self):
        """Ban non admin."""
        url = '/api/plugin/'
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertHttpForbidden(r)

