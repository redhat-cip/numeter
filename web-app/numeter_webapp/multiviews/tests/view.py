"""
View model tests module.
"""

from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from core.models import Host
from core.tests.utils import set_storage, set_users
from multiviews.models import View, Event
from multiviews.tests.utils import create_view, create_event


class View_Manager_user_filter_Test(LiveServerTestCase):
    """
    Test filter view by his users and groups attributes.
    """
    @set_storage(extras=['host','plugin','source'])
    @set_users()
    def setUp(self):
        pass

    def test_grant_to_super_user(self):
        """Superuser access to every views."""
        self.view = create_view(self.host)
        views = View.objects.user_filter(self.admin)
        self.assertEqual(views.count(), 1, "Superuser can't access to a view")

    def test_grant_to_simple_user_with_his_user_view(self):
        """User access to his own view."""
        self.view = create_view(self.host, self.user)
        views = View.objects.user_filter(self.user)
        self.assertEqual(views.count(), 1, "User can't access to his view")

    def test_grant_to_simple_user_with_his_group_view(self):
        """User access to his group view."""
        self.view = create_view(self.host, group=self.group)
        views = View.objects.user_filter(self.user)
        self.assertEqual(views.count(), 1, "User can't access to his group view")

    def test_grant_to_simple_user_with_user_and_group_view(self):
        """User access to his group view."""
        self.view = create_view(self.host, self.user, self.group)
        views = View.objects.user_filter(self.user)
        self.assertEqual(views.count(), 1, "User can't access to his group and user view")

    def test_forbid_to_simple_user_with_not_owned_view(self):
        """User doesn't access to a not owned view."""
        self.view = create_view(self.host)
        views = View.objects.user_filter(self.user)
        self.assertEqual(views.count(), 0, "User can access to a not owned view.")

    def test_forbid_to_simple_user_with_foreign_user_view(self):
        """User doesn't access to a view owned by other user."""
        self.view = create_view(self.host, self.user2)
        views = View.objects.user_filter(self.user)
        self.assertEqual(views.count(), 0, "User can access to a view owned by other user.")

    def test_forbid_to_simple_user_with_foreign_group_view(self):
        """User doesn't access to a view owned by other group."""
        self.view = create_view(self.host, group=self.group)
        views = View.objects.user_filter(self.user2)
        self.assertEqual(views.count(), 0, "User can access to a view owned by other group.")


class View_Test(LiveServerTestCase):
    @set_storage(extras=['host','plugin','source'])
    def setUp(self):
        self.view = create_view()

#     def test_get_events(self):
#         """Get event(s) for a view.""" 
#         event = create_event()
#         events = self.view.get_events()
#         self.assertTrue(events, "Empty result.")

    def test_get_data(self):
        """Retrieve data."""
        data = {'res':'Daily'}
        r = self.view.get_data(**data)
        self.assertIsInstance(r, list, "Invalide response type, should be list.")

    def test_get_extended_data(self):
        """Retrieve extended data."""
        data = {'res':'Daily'}
        r = self.view.get_data(**data)
        self.assertIsInstance(r, list, "Invalide response type, should be dict.")
