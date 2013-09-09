from django.test import TestCase
from core.models import User, Group, Host


class Access_TestCase(TestCase):
    fixtures = ['test_users.json','test_groups','test_hosts.json']

    def test_superuser_can_all(self):
        admin = User.objects.get(pk=1)
        # Access to host
        host = Host.objects.get(pk=1)
        r = admin.has_access(host)
        self.assertTrue(r, "Superuser can't access to hosts.")
    
        # Access to user
        user = User.objects.get(pk=2)
        r = admin.has_access(user)
        self.assertTrue(r, "Superuser can't access to users.")
        
        # Access to group
        group = Group.objects.get(pk=1)
        r = admin.has_access(group)
        self.assertTrue(r, "Superuser can't access to groups.")

    def test_access_to_own_group(self):
        user = User.objects.get(pk=2)
        # Access to host
        host = Host.objects.get(pk=1)
        r = user.has_access(host)
        self.assertTrue(r, "Simple user can't access to his hosts.")

        # Access to user
        r = user.has_access(user)
        self.assertTrue(r, "Simple user can't access to himself.")
        
        # Access to group
        group = Group.objects.get(pk=1)
        r = user.has_access(group)
        self.assertTrue(r, "Simple user can't access to his groups.")

    def test_access_to_other_group(self):
        user = User.objects.get(pk=2)
        # Access to host
        host = Host.objects.get(pk=2)
        r = user.has_access(host)
        self.assertFalse(r, "Simple user can access to other group's hosts.")

        # Access to user
        user2 = User.objects.get(pk=3)
        r = user.has_access(user2)
        self.assertFalse(r, "Simple user can access to users.")
        
        # Access to group
        group = Group.objects.get(pk=2)
        r = user.has_access(group)
        self.assertFalse(r, "Simple user can access to others groups.")
