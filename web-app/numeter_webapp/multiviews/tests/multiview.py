"""
Multiview model tests module.
"""

from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from core.models import Host, Plugin, Data_Source
from core.tests.utils import set_storage, set_users
from multiviews.models import Multiview
from multiviews.tests.utils import set_views, create_multiview, create_event


class Multiview_Manager_user_filter_Test(LiveServerTestCase):
    """
    Test filter multiview by his users and groups attributes.
    """
    @set_storage(extras=['host','plugin','source'])
    @set_users()
    @set_views()
    def setUp(self):
        pass

    def test_grant_to_super_user(self):
        """Superuser access to every multiviews."""
        create_multiview(self.host)
        multiviews = Multiview.objects.user_filter(self.admin)
        self.assertEqual(multiviews.count(), 1, "Superuser can't access to a multiview")

    def test_grant_to_simple_user_with_his_user_view(self):
        """User access to his own multiview."""
        create_multiview(self.host, self.user)
        multiviews = Multiview.objects.user_filter(self.user)
        self.assertEqual(multiviews.count(), 1, "User can't access to his multiview")

    def test_grant_to_simple_user_with_his_group_multiview(self):
        """User access to his group multiview."""
        create_multiview(self.host, group=self.group)
        multiviews = Multiview.objects.user_filter(self.user)
        self.assertEqual(multiviews.count(), 1, "User can't access to his group multiview")

    def test_grant_to_simple_user_with_user_and_group_multiview(self):
        """User access to his group multiview."""
        create_multiview(self.host, self.user, self.group)
        multiviews = Multiview.objects.user_filter(self.user)
        self.assertEqual(multiviews.count(), 1, "User can't access to his group and user multiview")

    def test_forbid_to_simple_user_with_not_owned_multiview(self):
        """User doesn't access to a not owned multiview."""
        create_multiview(self.host)
        multiviews = Multiview.objects.user_filter(self.user)
        self.assertEqual(multiviews.count(), 0, "User can access to a not owned multiview.")

    def test_forbid_to_simple_user_with_foreign_user_multiview(self):
        """User doesn't access to a multiview owned by other user."""
        create_multiview(self.host, self.user2)
        multiviews = Multiview.objects.user_filter(self.user)
        self.assertEqual(multiviews.count(), 0, "User can access to a multiview owned by other user.")

    def test_forbid_to_simple_user_with_foreign_group_multiview(self):
        """User doesn't access to a multiview owned by other group."""
        create_multiview(self.host, group=self.group)
        multiviews = Multiview.objects.user_filter(self.user2)
        self.assertEqual(multiviews.count(), 0, "User can access to a multiview owned by other group.")


class Multiview_Test(LiveServerTestCase):
    @set_storage(extras=['host','plugin','source'])
    @set_views()
    def setUp(self):
        pass
