from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from multiviews.models import Event
from hashlib import md5


class View_Manager(models.Manager):
    def user_filter(self, user):
        """Filter views authorized for a given user."""
        if user.is_superuser:
            return self.all()
        else:
            return self.filter(sources__plugin__host__group__in=user.groups.all()).distinct()

    def web_filter(self, q):
        """Extended search from a string."""
        views = self.filter(
            Q(name__icontains=q) |
            Q(sources__name__icontains=q)
        ).distinct()
        return views

    def user_web_filter(self, q, user):
        """Extended search from a string only on authorized views."""
        views = self.web_filter(q)
        if user.is_superuser:
            return views
        return views.filter(sources__plugin__host__group__in=user.groups.all()).distinct()


class View(models.Model):
    """
    Graphic unit with assembled data sources.
    It mays include warning and critical line.
    """
    name = models.CharField(_('name'), max_length=300)
    sources = models.ManyToManyField('core.Data_Source')
    comment = models.TextField(_('comment'), max_length=3000, blank=True, null=True)
    warning = models.IntegerField(blank=True, null=True)
    critical = models.IntegerField(blank=True, null=True)

    objects = View_Manager()
    class Meta:
        app_label = 'multiviews'
        ordering = ('name',)
        verbose_name = 'view'
        verbose_name_plural = 'views'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('view', args=[self.id])

    def get_add_url(self):
        return reverse('view add')

    def get_update_url(self):
        if not self.id:
            return reverse('view add')
        return reverse('view update', args=[self.id])

    def get_delete_url(self):
        return reverse('view delete', args=[self.id])

    def get_list_url(self):
        return reverse('view list')

    def get_data_url(self):
        return reverse('view data', args=[self.id])

    def get_events(self):
        """Return QuerySet of Events of this view."""
        host_ids = self.sources.values_list('plugin__host')
        return Event.objects.filter(hosts__id__in=host_ids)

    def get_data(self, res='Daily'):
        """
        Get sources' data from storage.
        """
        data = {'res':res}
        datas = []
        for source in self.sources.all():
            datas.append(source.get_data())
        return zip(*datas)

    def get_extended_data(self, res='Daily'):
        datas = []
        data = {'res':res}
        r_data = {
            'labels':['Date'],
            'colors':[],
            'name':self.name,
            'datas':[],
            'type':'view',
            'id':self.id,
            'source_ids':[],
        }
        # Get All host and Events
        #host_pk = self.sources.all().values_list('plugin__host')
        #events = Event.objects.filter(hosts__pk__in=hosts_pk)
        #r_data['event'] = events.values('name','date','comment')
        # Set metadata
        # Set labels for warning lines
        if self.warning is not None:
            r_data['labels'].append('warning')
            r_data['colors'].append("#febf01")
        if self.critical is not None:
            r_data['labels'].append('critical')
            r_data['colors'].append("#FF3434")
        ## Set datas
        # Get all data
        for s in self.sources.all():
            r = s.get_data(**data)
            unique_name = '%s %s' % (s.plugin.host.name, s.name)
            r_data['labels'].append(unique_name)
            datas.append(r['DATAS'][s.name])
            r_data['colors'].append("#%s" % md5(unique_name).hexdigest()[:6])
            r_data['source_ids'].append(s.id)
        # Skip if there's no data
        if not datas:
            return r_data
        # Add warning and critical line
        if self.critical is not None:
            critical_data = [self.critical] * len(datas[0])
            datas.insert(0, critical_data)
        if self.warning is not None:
            warning_data = [self.warning] * len(datas[0])
            datas.insert(0, warning_data)

        # Append empty datas if there's no
        if not 'r' in locals():
            r_data['datas'].append( (int(now().strftime('%s'))*1000,) )
        # Walk on date for mix datas
        else:
            cur_date = r['TS_start']
            step = r['TS_step']
            for v in zip(*datas):
                r_data['datas'].append((cur_date,) + v)
                cur_date += step
        return r_data
