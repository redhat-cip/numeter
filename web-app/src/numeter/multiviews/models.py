from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta
from time import mktime


class Plugin_Manager(models.Manager):
    def create_host_plugins(seld, host):
        plugins = host.get_plugins()
        new_ps = []
        for p in plugins:
            new_p = Plugin.objects.create(name=p['Plugin'], host=host)
            new_ps.append(new_p)
        return new_ps


class Plugin(models.Model):
    name = models.CharField(_('name'), max_length=300)
    host = models.ForeignKey('core.Host')

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

    def get_add_url(self):
        return reverse('plugin add')

    def get_update_url(self):
        return reverse('plugin update', args=[self.id])

    def get_delete_url(self):
        return reverse('plugin delete', args=[self.id])

    def get_list_url(self):
        return reverse('plugin list')

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


class Data_Source(models.Model):
    name = models.CharField(_('name'), max_length=300)
    plugin = models.ForeignKey(Plugin)

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


class View(models.Model):
    name = models.CharField(_('name'), max_length=300)
    sources = models.ManyToManyField(Data_Source)
    comment = models.TextField(_('comment'), max_length=3000, blank=True, null=True)

    class Meta:
        app_label = 'multiviews'
        ordering = ('name',)
        verbose_name = 'view'
        verbose_name_plural = 'views'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('multiview', args=[self.id])

    def get_add_url(self):
        return reverse('multiview add')

    def get_update_url(self):
        return reverse('multiview update', args=[self.id])

    def get_delete_url(self):
        return reverse('multiview delete', args=[self.id])

    def get_list_url(self):
        return reverse('multiview list')

    def get_data_url(self):
        return reverse('view data', args=[self.id])

    def get_data(self, ds='nice', res='Daily'):
        data = {'res':res}
        datas = []
        for source in self.sources.all():
            datas.append(source.get_data())
        return zip(*datas)

    def get_data_dygraph(self, res='Daily'):
        datas = {}
        data = {'res':res}
        r_data = {'labels':['Date'], 'name':self.name, 'datas':[]}
        if not self.sources.exists():
            return r_data
        # Get all data
        for s in self.sources.all():
            r = s.get_data(**data)
            unique_name = '%s %s' % (s.plugin.host.name, s.name)
            r_data['labels'].append(unique_name)
            datas[unique_name] = r['DATAS'][s.name]
        # Walk on date for mix datas
        cur_date = r['TS_start']
        step = r['TS_step']
        print datas
        for v in zip(*datas.values()):
            r_data['datas'].append((cur_date,) + v)
            cur_date += step
        return r_data


class Multiview_Manager(models.Manager):
    def get_user_multiview(self, user):
        if user.is_superuser:
            return self.all()
        else:
            return self.filter(views__plugins__host__group__in=user.groups.all())


class Multiview(models.Model):
    name = models.CharField(_('name'), max_length=300)
    views = models.ManyToManyField(View)

    objects = Multiview_Manager()
    class Meta:
        app_label = 'multiviews'
        ordering = ('name',)
        verbose_name = 'multiview'
        verbose_name_plural = 'multiviews'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('multiview', args=[self.id])

    def get_add_url(self):
        return reverse('multiview add')

    def get_update_url(self):
        return reverse('multiview update', args=[self.id])

    def get_delete_url(self):
        return reverse('multiview delete', args=[self.id])

    def get_list_url(self):
        return reverse('multiview list')


class Event(models.Model):
    name = models.CharField(_('name'), max_length=300)
    plugin = models.ForeignKey(Plugin)
    comment = models.TextField(_('comment'), max_length=3000, blank=True, null=True)
    date = models.DateTimeField()

    class Meta:
        app_label = 'multiviews'
        ordering = ('name',)
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
