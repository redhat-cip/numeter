from django.test import TestCase
from core.models import User, Group, Host
from core.utils.perms import has_perm


class Perms_Test(TestCase):
    fixtures = ['test_users.json','test_groups.json','test_hosts.json']

    def setUp(self):
        self.admin = User.objects.get(username='root')
        self.user = User.objects.get(username='Client')


    def test_superuser_perm(self):
        """Superuser has all access."""
        r = has_perm(self.admin, Group, '1')
        self.assertTrue(r, "Superuser hasn't perms.")
        r = has_perm(self.admin, Group, '2')
        self.assertTrue(r, "Superuser hasn't perms.")
        r = has_perm(self.admin, Group, None)
        self.assertTrue(r, "Superuser hasn't perms.")

        r = has_perm(self.admin, Host, '1')
        self.assertTrue(r, "Superuser hasn't perms.")
        r = has_perm(self.admin, Host, '2')
        self.assertTrue(r, "Superuser hasn't perms.")
        r = has_perm(self.admin, Host, '3')
        self.assertTrue(r, "Superuser hasn't perms.")

    def test_user_perm(self):
        """Simple user can only access to his group."""
        r = has_perm(self.user, Group, '1')
        self.assertTrue(r, "User hasn't perms.")
        r = has_perm(self.user, Group, '2')
        self.assertFalse(r, "User has bad perms.")
        r = has_perm(self.user, Group, None)
        self.assertFalse(r, "User has bad perms.")

        r = has_perm(self.user, Host, '1')
        self.assertTrue(r, "User can't access to his group's hosts.")
        r = has_perm(self.user, Host, '2')
        self.assertFalse(r, "Simple user can access to others group's Host")
        r = has_perm(self.user, Host, '3')
        self.assertFalse(r, "Simple user can access to not grouped host.")
