from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from core.models import Data_Source


class Plugin_Manager(models.Manager):
    def web_filter(self, q):
        """Search string in plugins' name or plugins' host's name."""
        return self.filter(
            Q(name__icontains=q) |
            Q(host__name__icontains=q)
        ).distinct()


class Plugin(models.Model):
    name = models.CharField(_('name'), max_length=300)
    host = models.ForeignKey('core.Host')
    comment = models.TextField(_('Comment'), max_length=3000, null=True, blank=True)

    objects = Plugin_Manager()
    class Meta:
        app_label = 'core'
        ordering = ('host','name')
        verbose_name = _('plugin')
        verbose_name_plural = _('plugins')
        unique_together = [('name','host')]

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

    def create_data_sources(self, source_names=[]):
        """
        Create sources from the given sources list.
        If not sources is given, all are created.
        """
        r = self.get_data_sources()
        new_ds = []
        for ds in r:
            if ds in source_names or source_names == []:
                if not Data_Source.objects.filter(name=ds, plugin=self).exists():
                    try:
                        new_d = Data_Source.objects.create(name=ds, plugin=self)
                        new_ds.append(new_d)
                    except:
                        pass
        return new_ds

    def get_data_sources(self):
        """
        Hard coding of self.host.get_plugin_data_sources.

        Return a list of data sources.
        """
        return self.host.get_plugin_data_sources(self.name)

    def get_data(self, **data):
        """
        Hard coding of self.host.get_data.

        Get plugin's data from storage.
        It is raw data from storage API.
        """
        data['plugin'] = self.name
        return self.host.get_data(**data)

    def get_unsaved_sources(self):
        """List source aren't in db."""
        sources = set(self.get_data_sources())
        if Data_Source.objects.filter(plugin=self).exists():
            saved = set(zip(*Data_Source.objects.filter(plugin=self).values_list('name'))[0])
        else:
            saved = set()
        return list(sources ^ saved)
