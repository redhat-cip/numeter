from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from multiviews.models import Data_Source


class Plugin_Manager(models.Manager):
    def create_from_host(self, host):
        plugins = host.get_plugins()
        new_ps = []
        for p in plugins:
            new_p = Plugin.objects.create(name=p['Plugin'], host=host)
            new_ps.append(new_p)
        return new_ps


class Plugin(models.Model):
    name = models.CharField(_('name'), max_length=300)
    host = models.ForeignKey('core.Host')
    comment = models.TextField(_('Comment'), max_length=3000, null=True, blank=True)

    objects = Plugin_Manager()
    class Meta:
        app_label = 'multiviews'
        ordering = ('host','name')
        verbose_name = _('plugin')
        verbose_name_plural = _('plugins')

    def __unicode__(self):
        return self.host.name + ' - ' + self.name

    def get_absolute_url(self):
        return reverse('plugin', args=[self.id])

    def get_update_url(self):
        return reverse('plugin update', args=[self.id])

    def get_delete_url(self):
        return reverse('plugin delete', args=[self.id])

    def get_list_url(self):
        return reverse('plugin list')

    def get_create_sources_url(self):
        return reverse('plugin create sources', args=[self.id])

    def create_data_sources(self):
        r = self.get_data_sources()
        new_ds = []
        for ds in r:
            new_d = Data_Source.objects.create(name=ds, plugin=self)
            new_ds.append(new_d)
        return new_ds

    def get_data_sources(self):
        return self.host.get_plugin_data_sources(self.name)

    def get_data(self, **data):
        data['plugin'] = self.name
        return self.host.get_data(**data)

