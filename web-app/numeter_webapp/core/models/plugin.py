from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from core.models import Data_Source
from core.models.utils import QuerySet


class Plugin_QuerySetManager(QuerySet):
    def user_filter(self, user):
        """Filters plugins authorized for a given user."""
        if user.is_superuser:
            return self.all()
        return self.filter(host__group__in=user.groups.all())

    def web_filter(self, q):
        """Extended search from a string."""
        return self.filter(
            Q(name__icontains=q) |
            Q(host__name__icontains=q)
        ).distinct()

    def user_web_filter(self, q, user):
        """Extended search from a string only on authorized plugin."""
        plugins = self.web_filter(q)
        if user.is_superuser:
            return plugins
        return plugins.filter(host__group__in=user.groups.all())


class Plugin(models.Model):
    name = models.CharField(_('name'), max_length=200)
    host = models.ForeignKey('core.Host')
    comment = models.TextField(_('Comment'), max_length=3000, null=True, blank=True)

    objects = Plugin_QuerySetManager.as_manager()
    class Meta:
        app_label = 'core'
        ordering = ('host','name')
        verbose_name = _('plugin')
        verbose_name_plural = _('plugins')
        unique_together = [('name','host')]

    def __unicode__(self):
        return self.host.name + ' - ' + self.name

    def user_has_perm(self, user):
        """
        Return if a user is allowed to access an instance.
        A user is allowed if super or in same host's group.
        """
        if user.is_superuser:
            return True
        return self.host.group in user.groups.all()

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

    def get_rest_list_url(self):
       return reverse('plugin-list') 

    def get_rest_detail_url(self):
       return reverse('plugin-detail', args=[self.id]) 

    def get_rest_create_sources_url(self):
        return reverse('plugin-create-sources', args=[self.id])

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
                else:
                    new_ds.append(Data_Source.objects.get(name=ds, plugin=self))
        return new_ds

    def get_data_sources(self):
        """
        Hard coding of self.host.get_plugin_data_sources.
        Return a list of sources' name.
        """
        return self.host.get_plugin_data_sources(self.name)

    def get_info(self):
        """
        Return info for the instancied plugin.
        """
        return self.host.get_plugin_info(self.name)

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
