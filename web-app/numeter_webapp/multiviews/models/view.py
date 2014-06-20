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

    def _create_view_infos_and_datas(self, res='Daily'):
        view_info = {
            'Describ': self.comment,
            'Plugin': self.name,
            'Title': self.name,
            'Infos': {},
        }
        all_colors = []
        source_ids = []
        view_datas = {'DATAS':{}}
        ## Walk on sources and set data
        for s in self.sources.all():
            source_ids.append(s.id)
            ## Make unique name for label and id
            #unique_name = '%s %s' % (s.plugin.host.name, s.name)
            source_info = s.get_info()
            source_info['label'] = s.__unicode__()
            source_info['id'] = s.__unicode__()
            # Get color
            color = source_info.get('color')
            # Make color uniq
            if color is not None:
                if color in all_colors :
                    color = '#' + md5(source_info['id']).hexdigest()[:6]
                    source_info['color'] = color
                all_colors.append(color)
            view_info['Infos'][s.__unicode__()] = source_info
            # Get datas
            source_data = s.get_data(res=res)
            view_datas['DATAS'][s.__unicode__()] = source_data['DATAS'][s.name]
            # Get first start Timestamp and step
            if view_datas.get('TS_start') is None:
                view_datas['TS_start'] = source_data['TS_start']
            if view_datas.get('TS_step') is None:
                view_datas['TS_step'] = source_data['TS_step']
        return source_ids, view_info, view_datas


    def get_extended_data(self, res='Daily'):
        (source_ids, view_infos, view_datas) = self._create_view_infos_and_datas(res=res)
        response_data = {
            'name': self.name,
            'datas': view_datas,
            'type': 'view',
            'id': self.id,
            'source_ids': source_ids,
            'infos': view_infos,
            'warning': self.warning,
            'critical': self.critical,
        }

        return response_data
