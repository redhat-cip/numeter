from django.utils.timezone import now
from core.models import Host, Data_Source
from multiviews.models import View, Multiview, Event


def create_view():
    """Fast create a view with the 2 first sources."""
    v = View(name="Test view")
    v.save()
    v.name = "Test view #%i" % v.id
    v.save()
    [ v.sources.add(s) for s in [ s[0] for s in Data_Source.objects.all().values_list('id')[:2] ] ] 
    return v


def create_multiview():
    """Fast create a multiview with the 2 first views."""
    m = Multiview(name="Test multiview")
    m.save()
    m.name = "Test multiview #%i" % m.id
    m.save()
    create_view()
    create_view()
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
