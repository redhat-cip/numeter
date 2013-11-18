from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from core.models.utils import QuerySet
from multiviews.models import Event
from hashlib import md5


class View_QuerySetManager(QuerySet):
    def user_filter(self, user):
        """Filter views authorized for a given user."""
        if user.is_superuser:
            return self.all()
        return self.filter(
            Q(users__in=[user]) |
            Q(groups__in=user.groups.all())
        ).distinct()

    def web_filter(self, q):
        """Extended search from a string."""
        return self.filter(
            Q(name__icontains=q) |
            Q(sources__name__icontains=q)
        ).distinct()

    def user_web_filter(self, q, user):
        """Extended search from a string only on authorized views."""
        views = self.web_filter(q)
        if user.is_superuser:
            return views
        return views.user_filter(user)


class View(models.Model):
    """
    Graphic unit with assembled data sources.
    It mays include warning and critical line.
    """
    name = models.CharField(_('name'), max_length=250)
    sources = models.ManyToManyField('core.Data_Source')
    comment = models.TextField(_('comment'), max_length=3000, blank=True, null=True)
    warning = models.IntegerField(blank=True, null=True)
    critical = models.IntegerField(blank=True, null=True)
    users = models.ManyToManyField('core.User', null=True, blank=True)
    groups = models.ManyToManyField('core.Group', null=True, blank=True)

    objects = View_QuerySetManager.as_manager()
    class Meta:
        app_label = 'multiviews'
        ordering = ('name',)
        verbose_name = 'view'
        verbose_name_plural = 'views'

    def __unicode__(self):
        return self.name

    def user_has_perm(self, user):
        """
        Return if a user is allowed to access an instance.
        A user is allowed if super or in same group's group or owned by him.
        """
        if user.is_superuser:
            return True
        return user in self.users.all() or bool( set(user.groups.all()) & set(self.groups.all()) )

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
        if not self.pk:
            return ''
        return reverse('view data', args=[self.id])

    def get_rest_list_url(self):
       return reverse('view-list') 

    def get_rest_detail_url(self):
       return reverse('view-detail', args=[self.id]) 

    def get_events(self):
        """Return QuerySet of Events of this view."""
        host_ids = self.sources.values_list('plugin__host')
        return Event.objects.filter(hosts__id__in=host_ids)

    def get_events_source_matching(self):
        """Return a dict with key/value = Source/Events."""
        match = {}
        for s in self.sources.all():
            match[s] = Event.objects.filter(hosts=s.plugin.host)
        return match

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
            'events':[],
            'infos':{},
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
        for s in self.sources.all():
            r = s.get_data(**data) # Get data
            # Make color
            unique_name = '%s %s' % (s.plugin.host.name, s.name)
            r_data['labels'].append(unique_name)
            r_data['colors'].append("#%s" % md5(unique_name).hexdigest()[:6])
            # Add name
            datas.append(r['DATAS'][s.name])
            r_data['source_ids'].append(s.id)
            # Add infos
            r_data['infos'][unique_name] = s.get_info()
        # Get Events
        events = self.get_events()
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
        # Add timestamp to data
        else:
            cur_date = r['TS_start']
            step = r['TS_step']
            # Walk on data and add date by step
            for v in zip(*datas):
                r_data['datas'].append((cur_date,) + v)
                # Add events with step_date
                #for e in events.in_step(cur_date, res).values('comment','short_text'):
                #    e['date'] = cur_date
                #    r_data['events'].append(e)
                cur_date += step
        return r_data
