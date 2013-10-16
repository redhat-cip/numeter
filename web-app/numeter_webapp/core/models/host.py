from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from core.models.utils import QuerySet
from datetime import datetime, timedelta
from time import mktime


class Host_QuerySetManager(QuerySet):
    """Custom Manager with extra methods."""
    def user_filter(self, user):
        """Filter hosts authorized for a given user."""
        if user.is_superuser:
            return self.all()
        return self.filter(group__in=user.groups.all())

    def web_filter(self, q):
        """Extended search from a string."""
        return self.filter(
            Q(name__icontains=q) |
            Q(storage__name__icontains=q) |
            Q(group__name__icontains=q) |
            Q(hostid__icontains=q)
        ).distinct()

    def user_web_filter(self, q, user):
        """Extended search from a string only on authorized sources."""
        hosts = self.web_filter(q)
        if user.is_superuser:
            return hosts
        return hosts.filter(plugin__host__group__in=user.groups.all())

class Host(models.Model):
    """
    Corresponding to an host on storage.
    """
    name = models.CharField(_('name'), max_length=200)
    hostid = models.CharField(_('ID on storage'), max_length=300)
    storage = models.ForeignKey('Storage')
    group = models.ForeignKey('core.Group', null=True, blank=True)

    objects = Host_QuerySetManager.as_manager()
    class Meta:
        app_label = 'core'
        ordering = ('group', 'storage', 'name','hostid')
        verbose_name = _('host')
        verbose_name_plural = _('hosts')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('host', args=[str(self.id)])

    def get_update_url(self):
        return reverse('host update', args=[str(self.id)])

    def get_delete_url(self):
        return reverse('host delete', args=[str(self.id)])

    def get_list_url(self):
        return reverse('host list')

    def get_plugins_url(self):
        return reverse('host plugins', args=[str(self.id)])

    def get_info(self):
        """
        Hard coding of self.storage.get_info.

        Return a dictionnary representing an host on storage.
        It is raw data from storage API.
        """
        return self.storage.get_info(self.hostid)

    def get_categories(self):
        """
        Hard coding of self.storage.get_categories.

        Return a list representing an host plugins' category.
        """
        return self.storage.get_categories(self.hostid)

    def get_plugins(self):
        """
        Hard coding of self.storage.get_plugins.

        Return a list representing an host's plugins.
        Modify storage's data before returning.
        """
        return self.storage.get_plugins(self.hostid)

    def get_plugin_list(self):
        """Return a list of plugin names."""
        return [ p['Plugin'] for p in self.get_plugins() ]

    def get_plugins_by_category(self, category):
        """
        Hard coding of self.storage.get_plugins_by_category.

        Get host's plugins by category from storage.
        """
        return self.storage.get_plugins_by_category(self.hostid, category)

    def get_plugin_data_sources(self, plugin):
        """
        Hard coding of self.storage.get_plugin_data_sources.

        Return a list of data sources of a plugin.
        """
        return self.storage.get_plugin_data_sources(self.hostid, plugin)

    def get_data(self, **data):
        """
        Hard coding of self.storage.get_data.

        Get plugin's data from storage.
        It is raw data from storage API.
        """
        data['hostid'] = self.hostid
        return self.storage.get_data(**data)

    def get_plugin_info(self, plugin):
        """Get sources infos."""
        for p in  self.get_plugins():
            if p['Plugin'] == plugin:
                return p['Infos']
        
    def get_extended_data(self, **data):
        data['hostid'] = self.hostid
        # Get data sources name
        data['ds'] = ','.join(self.get_plugin_data_sources(data['plugin']))
        r = self.get_data(**data)
        # Dict sent in AJAX
        r_data = {
            'labels': ['Date'],
            'name': data['plugin'].lower(),
            'datas': [],
            'infos': self.get_plugin_info(data['plugin'])
        }
        r_data['labels'].extend(self.get_plugin_data_sources(data['plugin']))

        step = timedelta(seconds=r.get('TS_step', 60))
        cur_date = datetime.fromtimestamp(r['TS_start'])
        for v in zip(*r['DATAS'].values()):
            r_data['datas'].append( (mktime(cur_date.timetuple()),) + v )
            cur_date += step
        return r_data

    def create_plugins(self, plugin_names=[], commit=True):
        """
        Create plugins from the given plugins list.
        If no plugin is given, all are created.
        """
        from core.models import Plugin
        plugins = self.get_plugin_list()
        new_ps = []
        for p in plugins:
            if p in plugin_names or plugin_names == []:
                if not Plugin.objects.filter(name=p, host=self).exists():
                    new_p = Plugin(name=p, host=self)
                    new_ps.append(new_p)
        if commit:
            [ p.save() for p in new_ps ]
        return new_ps

    def get_unsaved_plugins(self):
        """List plugins aren't in db."""
        from core.models import Plugin
        plugins = set(self.get_plugin_list())
        saved_plugins = Plugin.objects.filter(host=self)
        if saved_plugins.exists():
            saved = set(zip(*saved_plugins.values_list('name'))[0])
        else:
            saved = set()
        return list(plugins ^ saved)
