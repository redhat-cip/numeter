from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from hashlib import md5


class View_Manager(models.Manager):
    def user_filter(self, user):
        """Filter views authorized for a given user."""
        if user.is_superuser:
            return self.all()
        else:
            return self.filter(sources__plugins__host__group__in=user.groups.all())

    def web_filter(self, q):
        """Extended search from a string."""
        views = self.filter(
            Q(name__icontains=q) |
            Q(sources__name__icontains=q)
        )
        return views

    def user_web_filter(self, q, user):
        """Extended search from a string only on authorized views."""
        views = self.web_filter(q)
        if user.is_superuser:
            return views
        return views.filter(sources__plugins__host__group__in=user.groups.all())


class View(models.Model):
    name = models.CharField(_('name'), max_length=300)
    sources = models.ManyToManyField('multiviews.Data_Source')
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

    def get_data(self, ds='nice', res='Daily'):
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
        # Set metadata
        # Set labels for warning lines
        if self.warning is not None:
            r_data['labels'].append('warning')
            r_data['colors'].append("#febf01")
        if self.critical is not None:
            r_data['labels'].append('critical')
            r_data['colors'].append("#FF3434")

        ## Set datas
        # Add warning and critical line
        if self.critical is not None:
            critical_data = [self.critical] * len(datas[0])
            datas.insert(0, critical_data)
        if self.warning is not None:
            warning_data = [self.warning] * len(datas[0])
            datas.insert(0, warning_data)
        # Get all data
        for s in self.sources.all():
            r = s.get_data(**data)
            unique_name = '%s %s' % (s.plugin.host.name, s.name)
            r_data['labels'].append(unique_name)
            datas.append(r['DATAS'][s.name])
            r_data['colors'].append("#%s" % md5(unique_name).hexdigest()[:6])
            r_data['source_ids'].append(s.id)

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


class Multiview_Manager(models.Manager):
    def user_filter(self, user):
        """Filter multiviews authorized for a given user."""
        if user.is_superuser:
            return self.all()
        else:
            return self.filter(views__plugins__host__group__in=user.groups.all())

    def web_filter(self, q):
        """Extended search from a string."""
        views = self.filter(
            Q(name__icontains=q) |
            Q(views__name__icontains=q)
        )
        return views

    def user_web_filter(self, q, user):
        """Extended search from a string only on authorized multiviews."""
        views = self.web_filter(q)
        if user.is_superuser:
            return views
        return views.filter(sources__plugins__host__group__in=user.groups.all())


class Multiview(models.Model):
    name = models.CharField(_('name'), max_length=300)
    views = models.ManyToManyField(View)
    comment = models.TextField(_('comment'), max_length=3000, blank=True, null=True)

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
        if not self.id:
            return reverse('multiview add')
        return reverse('multiview update', args=[self.id])

    def get_delete_url(self):
        return reverse('multiview delete', args=[self.id])

    def get_list_url(self):
        return reverse('multiview list')

    def get_customize_edit_url(self):
        return reverse('multiviews customize multiview edit', args=[self.id])


class Event(models.Model):
    name = models.CharField(_('name'), max_length=300)
    source = models.ForeignKey('multiviews.Data_Source')
    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    comment = models.TextField(_('comment'), max_length=3000, blank=True, null=True)

    class Meta:
        app_label = 'multiviews'
        ordering = ('source__plugin__host__name','name')
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

