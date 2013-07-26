from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


class Data_Source(models.Model):
    name = models.CharField(_('name'), max_length=300)
    plugin = models.ForeignKey('multiviews.Plugin')
    comment = models.TextField(_('Comment'), max_length=3000, null=True, blank=True)

    class Meta:
        app_label = 'multiviews'
        ordering = ('plugin','name')
        verbose_name = _('data source')
        verbose_name_plural = _('data_sources')

    def __unicode__(self):
        return '%s - %s - %s' % (self.plugin.host.name, self.plugin.name, self.name)

    def get_absolute_url(self):
        return reverse('source', args=[self.id])

    def get_update_url(self):
        return reverse('source update', args=[self.id])

    def get_delete_url(self):
        return reverse('source delete', args=[self.id])

    def get_list_url(self):
        return reverse('source list')

    def get_data(self, **data):
        data['plugin'] = self.plugin.name
        data['ds'] = self.name
        return self.plugin.host.get_data(**data)
