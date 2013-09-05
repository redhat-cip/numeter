from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from core.models.storage import RESOLUTION_STEP
from datetime import datetime, timedelta


class Event_Manager(models.Manager):
    def get_queryset(self):
        """Use Event_QuerySet."""
        return Event_QuerySet(self.model)

    def user_filter(self, user):
        """Filter events authorized for a given user."""
        if user.is_superuser:
            return self.all()
        else:
            return self.filter(hosts__groups__in=user.groups.all())

    def web_filter(self, q):
        """Extended search from a string."""
        return self.filter(
            Q(name__icontains=q) |
            Q(short_text=q) |
            Q(hosts__name=q)
        ).distinct()

    def user_web_filter(self, q, user):
        """Extended search from a string only on authorized events."""
        events = self.web_filter(q)
        if user.is_superuser:
            return events
        else:
            return events.filter(hosts__groups=user.groups.all())

class Event_QuerySet(models.query.QuerySet):
    """QuerySet with extras method."""
    def in_step(self, timestamp, res):
        """Filter events in a step defined by a timestamp and a resolution."""
        margin = timedelta(seconds=RESOLUTION_STEP[res]*60)
        date = datetime.fromtimestamp(timestamp)
        return self.filter(date__gte=date, date__lt=date+margin)


class Event(models.Model):
    name = models.CharField(_('name'), max_length=300)
    short_text = models.CharField(_('short text'), max_length=20, blank=True, null=True)
    hosts = models.ManyToManyField('core.host')
    date = models.DateTimeField(_('date'), default=now, blank=True, null=True)
    comment = models.TextField(_('comment'), max_length=3000, blank=True, null=True)

    objects = Event_Manager()
    class Meta:
        app_label = 'multiviews'
        ordering = ('date','name')
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('event', args=[self.id])

    def get_add_url(self):
        return reverse('event add')

    def get_update_url(self):
        if not self.id:
            return self.get_add_url()
        return reverse('event update', args=[self.id])

    def get_delete_url(self):
        return reverse('event delete', args=[self.id])

    def get_list_url(self):
        return reverse('event list')
