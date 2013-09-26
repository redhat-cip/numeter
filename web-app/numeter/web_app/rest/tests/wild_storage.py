from tastypie.test import ResourceTestCase
from core.tests.utils import set_storage, set_users
from core.models import Host, Plugin


class Wild_Storage_Test(ResourceTestCase):
    """
    Test wild storage.
    It should have the same behavor as Storage API.
    """
    @set_users()
    @set_storage(extras=['host','plugin'])
    def setUp(self):
        super(Wild_Storage_Test, self).setUp()

    def get_credentials(self):
        return self.create_basic(username=self.admin, password='toto')

    def test_hosts(self):
        """Get all storage's host list."""
        url = '/wild_storage/hosts'
        r = self.api_client.get(url)
        self.assertValidJSONResponse(r)

    def test_hinfo(self):
        """Get host's info."""
        url = '/wild_storage/hinfo'
        host = Host.objects.all()[0]
        data = {'host': host.hostid}
        r = self.api_client.get(url, data=data)
        self.assertValidJSONResponse(r)

    def test_list(self):
        """Get host's plugin list."""
        url = '/wild_storage/list'
        host = Host.objects.all()[0]
        data = {'host': host.hostid}
        r = self.api_client.get(url, data=data)
        self.assertValidJSONResponse(r)

    def test_data(self):
        """Get plugin's data."""
        url = '/wild_storage/list'
        host = Host.objects.all()[0]
        plugin = Plugin.objects.filter(host=host)[0]
        data = {
          'host': host.hostid,
          'plugin': plugin.name,
          'ds': ','.join(plugin.get_data_sources()),
          'res': 'Daily',
        }
        r = self.api_client.get(url, data=data)
        self.assertValidJSONResponse(r)
