from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta
from time import mktime


class Plugin(models.Model):
    name = models.CharField(_('name'), max_length=300)
    host = models.ForeignKey('core.Host')

    class Meta:
        app_label = 'multiviews'
        ordering = ('name',)
        verbose_name = _('plugin')
        verbose_name_plural = _('plugins')

    def __unicode__(self):
        return self.name

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

    def get_data(self, **data):
        data['plugin'] = self.name
        return self.host.get_data(**data)


class Multiviews_Manager(models.Manager):
    def get_user_multiview(self, user):
        if user.is_superuser:
            return self.all()
        else:
            return self.filter(plugins__host__group__in=user.groups.all())

class Multiview(models.Model):
    name = models.CharField(_('name'), max_length=300)
    plugins = models.ManyToManyField(Plugin)
    comment = models.TextField(_('comment'), max_length=3000, blank=True, null=True)

    objects = Multiviews_Manager()
    class Meta:
        app_label = 'multiviews'
        ordering = ('name',)
        verbose_name = 'Multiview'
        verbose_name_plural = 'Multiviews'

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
        data = {'ds':ds,'res':res}
        datas = []
        for plugin in self.plugins.all():
            data['plugin'] = plugin.name
            datas.append(plugin.get_data(**data)['DATAS']['nice'])
        return zip(*datas)

    def get_data_dygraph(self, ds='nice', res='Daily'):
        start_dates ={}
        datas = {}
        data = {'ds':ds,'res':res}
        r_data = {'labels':['Date'], 'name':self.name, 'datas':[]}
        # Get all data
        for p in self.plugins.all():
            r = p.get_data(**data)
            r_data['labels'].append(p.name)
            start_dates[p.name] = datetime.fromtimestamp(r['TS_start'])
            datas[p.name] = r['DATAS']['nice']
        # Walk on date for mix datas
        start_date = cur_date = min(start_dates.values())
        step = timedelta(seconds=r['TS_step'])
        for v in zip(*datas.values()):
            r_data['datas'].append((mktime(cur_date.timetuple()),) + v)
            cur_date += step
        return r_data

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
