from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


class Data_Source(models.Model):
    name = models.CharField(_('name'), max_length=300)
    plugin = models.ForeignKey('multiviews.Plugin')

    class Meta:
        app_label = 'multiviews'
        ordering = ('plugin','name')
        verbose_name = _('data source')
        verbose_name_plural = _('data_sources')

    def __unicode__(self):
        return '%s - %s - %s' % (self.plugin.host.name, self.plugin.name, self.name)

    def get_data(self, **data):
        data['plugin'] = self.plugin.name
        data['ds'] = self.name
        return self.plugin.host.get_data(**data)
