from tastypie.test import ResourceTestCase
from core.tests.utils import set_users
from core.models import Group


class Group_Test(ResourceTestCase):
    """
    Tests for group management API.
    Only available for admins.
    """
    @set_users()
    def setUp(self):
        super(Group_Test, self).setUp()

    def get_credentials(self):
        return self.create_basic('root', 'toto')

    def test_get_list(self):
        """Get list of groups."""
        url = '/api/group/'
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertValidJSONResponse(r)

    def test_get_detail(self):
        """Get group's detail."""
        url = '/api/group/%i/' % self.admin.pk
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertValidJSONResponse(r)

    def test_post(self):
        """Create a group."""
        url = '/api/group/'
        data = { 'name': 'new group' }
        r = self.api_client.post(url, data=data, authentication=self.get_credentials())
        self.assertHttpCreated(r)
        self.assertTrue(Group.objects.filter(name='new group').exists(), "Group hasn't been created")

    def test_patch(self):
        """Update a group."""
        url = '/api/group/%i/' % self.admin.pk
        data = { 'name': 'roott' }
        r = self.api_client.patch(url, data=data, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertEqual(Group.objects.get(pk=1).name, 'roott', "Data are unchanged.")

    def test_delete(self):
        """Delete a group."""
        url = '/api/group/%i/' % self.group.pk
        r = self.api_client.delete(url, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertFalse(Group.objects.filter(pk=self.group.pk).exists(), "Group hasn't been deleted.")

    def test_delete_list(self):
        """Delete a group list."""
        url = '/api/group/'
        data = {
          'deleted_objects': [
            '/api/group/%i/' % self.group.pk,
          ],
          'objects':[],
        }
        r = self.api_client.patch(url, data=data, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertFalse(Group.objects.filter(pk=self.group.pk).exists(), "Group hasn't been deleted.")


class Group_Forbidden_Test(ResourceTestCase):
    """
    Tests for unauthorized access.
    """
    @set_users()
    def setUp(self):
        super(Group_Forbidden_Test, self).setUp()

    def get_credentials(self):
        return self.create_basic('group', 'toto')

    def test_anonymous(self):
        """Ban anonymous."""
        url = '/api/group/'
        r = self.api_client.get(url)
        self.assertHttpUnauthorized(r)

    def test_simple_user(self):
        """Ban non admin."""
        url = '/api/group/'
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertHttpForbidden(r)

