from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from core.models import Host
from core.models.utils import QuerySet
from hashlib import md5


class Data_Source_QuerySetManager(QuerySet):
    def user_filter(self, user):
        """Filters source authorized for a given user."""
        if user.is_superuser:
            return self.all()
        return self.filter(plugin__host__group__in=user.groups.all())

    def web_filter(self, q):
        """Extended search from a string."""
        return self.filter(
            Q(name__icontains=q) |
            Q(plugin__name__icontains=q) |
            Q(plugin__host__name__icontains=q)
        ).distinct()

    def user_web_filter(self, q, user):
        """Extended search from a string only on authorized sources."""
        sources = self.web_filter(q)
        if user.is_superuser:
            return sources
        return sources.filter(plugin__host__group__in=user.groups.all())

    def full_create(self, POST):
        """Create sources and plugin if doesn't exist."""
        from core.models import Plugin
        host = Host.objects.get(hostid=POST['host'])
        # Check if plugin exists in storage and get_or_create
        if POST['plugin'] in host.get_plugin_list():
            plugin, created = Plugin.objects.get_or_create(host=host, name=POST['plugin'])
        else:
            raise ValueError('No existing plugin for this name and this host.')
        # Check if source exists in storage and create
        sources = []
        for source in POST.getlist('sources[]'):
            if not self.filter(name=source, plugin=plugin).exists() and \
                    source in plugin.get_data_sources():
                sources.append(self.create(name=source, plugin=plugin))
        return sources


class Data_Source(models.Model):
    """Plugin's data source, more often called shortly source."""
    name = models.CharField(_('name'), max_length=300)
    # short_name = models.CharField(_('shortname'), max_length=50)
    plugin = models.ForeignKey('core.Plugin')
    comment = models.TextField(_('Comment'), max_length=3000, null=True, blank=True)
    # description = models.TextField(_('Long description'), max_length=1000, null=True, Blank=True)

    objects = Data_Source_QuerySetManager.as_manager()
    class Meta:
        app_label = 'core'
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
        """
        Hard coding of self.host.get_data.

        Get plugin's data from storage.
        It is raw data from storage API.
        """
        data['plugin'] = self.plugin.name
        data['ds'] = self.name
        return self.plugin.host.get_data(**data)

    def get_extended_data(self, res='Daily'):
        """
        Make extended data for graphic library.
        Set more options than simple storage API like time.
        """
        datas = []
        data = {'res':res}
        r_data = {
            'labels':['Date'],
            'colors':[],
            'name':self.name,
            'datas':[]
        }
        # Get all data
        r = self.get_data(**data)
        r_data['labels'].append(self.name)
        datas.append(r['DATAS'][self.name])
        r_data['colors'].append("#%s" % md5(self.name).hexdigest()[:6])
        # Walk on date for mix datas
        cur_date = r['TS_start']
        step = r['TS_step']
        for v in zip(*datas):
            r_data['datas'].append((cur_date,) + v)
            cur_date += step
        return r_data

    def make_HTML_color(self):
        """Make a unique HTML color from source, plugin and host's names."""
        return md5(self.name+self.plugin.name+self.plugin.host.name).hexdigest()[:6]
