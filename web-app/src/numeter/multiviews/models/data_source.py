from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from hashlib import md5


class Data_Source_Manager(models.Manager):
    def user_filter(self, user):
        """Filter source authorized for a given user."""
        if user.is_superuser:
            return self.all()
        else:
            return self.filter(plugins__host__group__in=user.groups.all())

    def web_filter(self, q):
        sources = self.filter(
            Q(name__icontains=q) |
            Q(plugin__name__icontains=q) |
            Q(plugin__host__name__icontains=q)
        )
        return sources

    def user_web_filter(self, q, user):
        """Filter source authorized for a given user."""
        sources = self.web_filter(q)
        if user.is_superuser:
            return sources
        else:
            return sources.filter(plugins__host__group__in=user.groups.all())


class Data_Source(models.Model):
    name = models.CharField(_('name'), max_length=300)
    plugin = models.ForeignKey('multiviews.Plugin')
    comment = models.TextField(_('Comment'), max_length=3000, null=True, blank=True)

    objects = Data_Source_Manager()
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

    def get_data_dygraph(self, res='Daily'):
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
        step = r['TS_step'] * 60
        for v in zip(*datas):
            r_data['datas'].append((cur_date,) + v)
            cur_date += step
        return r_data
