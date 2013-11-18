"""
multiviews tests common objects module.
"""

from django.utils.timezone import now
from django.utils.decorators import available_attrs
from core.models import Host, Data_Source
from multiviews.models import View, Multiview, Event
from functools import wraps


def create_view(host=None, user=None, group=None):
    """
    Fast create a view with the 2 first sources.
    If ``host`` is specified, choose its sources.
    If ``user`` is specified, set as his.
    If ``group`` is specified, set as its.
    """
    host = host or Host.objects.all()[0]
    v = View(name="Test view")
    v.save()
    v.name = "Test view #%i" % v.id
    if user:
        v.users.add(user)
    if group:
        v.groups.add(group)
    v.save()
    [ v.sources.add(s) for s in [ s[0] for s in Data_Source.objects.filter(plugin__host=host).values_list('id')[:2] ] ] 
    return v


def create_multiview(host=None, user=None, group=None):
    """
    Fast create a multiview with the 2 first view.
    If ``host`` is specified, choose its sources.
    If ``user`` is specified, set as his.
    If ``group`` is specified, set as its.
    """
    m = Multiview(name="Test multiview")
    m.save()
    m.name = "Test multiview #%i" % m.id
    m.save()
    create_view(host=None)
    create_view(host=None)
    if user:
        m.users.add(user)
    if group:
        m.groups.add(group)
    [ m.views.add(v) for v in [ v[0] for v in View.objects.all().values_list('id')[:2] ] ] 
    return m


def create_event():
    """Fast create an event with the 2 first hosts."""
    e = Event(name='Test event', date=now())
    e.save()
    e.name = "Test event #%i" % e.id
    e.save()
    [ e.hosts.add(h) for h in [ h[0] for h in Host.objects.all().values_list('id')[:2] ] ] 
    return e


def set_views():
    """
    Create 3 views, a not owned, owned by a user,
    and owned by group.
    """
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(self, *args, **kwargs):
            self.view_not_owned = create_view()
            if hasattr(self, 'user'):
                self.view_user = create_view(user=self.user)
                self.view_group = create_view(group=self.group)
            return func(self, *args, **kwargs)
        return inner
    return decorator


def set_multiviews():
    """
    Create 3 multiviews, a not owned, owned by a user,
    and owned by group.
    """
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(self, *args, **kwargs):
            self.multiview_not_owned = create_multiview()
            if hasattr(self, 'user'):
                self.multiview_user = create_multiview(user=self.user)
                self.multiview_group = create_multiview(group=self.group)
            return func(self, *args, **kwargs)
        return inner
    return decorator
