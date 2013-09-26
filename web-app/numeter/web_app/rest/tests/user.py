from tastypie.test import ResourceTestCase
from core.tests.utils import set_users
from core.models import User


class User_Test(ResourceTestCase):
    """
    Tests for user management API.
    Only available for admins.
    """
    @set_users()
    def setUp(self):
        super(User_Test, self).setUp()

    def get_credentials(self):
        return self.create_basic('root', 'toto')

    def test_get_list(self):
        """Get list of users."""
        url = '/api/user/'
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertValidJSONResponse(r)
        # Get set of user
        url = '/api/user/set/1;3/'
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertValidJSONResponse(r)

    def test_get_detail(self):
        """Get user's detail."""
        url = '/api/user/%i/' % self.admin.pk
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertValidJSONResponse(r)

    def test_post(self):
        """Create a user."""
        url = '/api/user/'
        data = {
          'username': 'new user',
          'password': 'pass',
        }
        r = self.api_client.post(url, data=data, authentication=self.get_credentials())
        self.assertHttpCreated(r)
        self.assertTrue(User.objects.filter(username='new user').exists(), "User hasn't been created")

    def test_patch(self):
        """Update a user."""
        url = '/api/user/%i/' % self.admin.pk
        data = { 'username': 'roott' }
        r = self.api_client.patch(url, data=data, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertEqual(User.objects.get(pk=1).username, 'roott', "Data are unchanged.")

    def test_delete(self):
        """Delete a user."""
        url = '/api/user/%i/' % self.user.pk
        r = self.api_client.delete(url, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertFalse(User.objects.filter(username='Client').exists(), "User hasn't been deleted.")

    def test_delete_list(self):
        """Delete a user list."""
        url = '/api/user/'
        data = {
          'deleted_objects': [
            '/api/user/%i/' % self.user.pk,
            '/api/user/%i/' % self.user2.pk,
          ],
          'objects':[],
        }
        r = self.api_client.patch(url, data=data, authentication=self.get_credentials())
        self.assertHttpAccepted(r)
        self.assertFalse(User.objects.filter(pk__in=[self.user.pk,self.user2.pk]).exists(), "Users haven't been deleted.")
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists(), "Wrong user hasn't been deleted.")


class User_Forbidden_Test(ResourceTestCase):
    """
    Tests for unauthorized access.
    """
    @set_users()
    def setUp(self):
        super(User_Forbidden_Test, self).setUp()

    def get_credentials(self):
        return self.create_basic('user', 'toto')

    def test_anonymous(self):
        """Ban anonymous."""
        url = '/api/user/'
        r = self.api_client.get(url)
        self.assertHttpUnauthorized(r)

    def test_simple_user(self):
        """Ban non admin."""
        url = '/api/user/'
        r = self.api_client.get(url, authentication=self.get_credentials())
        self.assertHttpForbidden(r)
