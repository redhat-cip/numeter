from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


class Event(models.Model):
    name = models.CharField(_('name'), max_length=300)
    hosts = models.ManyToManyField('core.host')
    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    comment = models.TextField(_('comment'), max_length=3000, blank=True, null=True)

    class Meta:
        app_label = 'multiviews'
        ordering = ('source__plugin__host__name','name')
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('Event', args=[self.id])

    def get_add_url(self):
        return reverse('Event add')

    def get_update_url(self):
        return reverse('Event update', args=[self.id])

    def get_delete_url(self):
        return reverse('Event delete', args=[self.id])

    def get_list_url(self):
        return reverse('Event list')

