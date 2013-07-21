from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from datetime import datetime, timedelta
from time import mktime

class Host(models.Model):
    """
    Corresponding to an host on storage.
    """
    name = models.CharField(_('name'), max_length=200)
    hostid = models.CharField(_('ID on storage'), max_length=300)
    storage = models.ForeignKey('Storage')
    group = models.ForeignKey('core.Group', null=True, blank=True)

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
        """Get host's info from storage."""
        return self.storage.get_info(self.hostid)

    def get_categories(self):
        """Get host's categories from storage."""
        return self.storage.get_categories(self.hostid)

    def get_plugins(self):
        """Get all host plugin's from storage."""
        return self.storage.get_plugins(self.hostid)

    def get_plugins_by_category(self, category):
        """Get host's plugins by category from storage."""
        return self.storage.get_plugins_by_category(self.hostid, category)

    def get_data(self, **data):
        """Get plugin's data from storage."""
        data['hostid'] = self.hostid
        return self.storage.get_data(**data)

    def get_data_dygraph(self, **data):
        data['hostid'] = self.hostid
        r = self.storage.get_data(**data)
        data = dict()
        start_date = datetime.fromtimestamp(r['TS_start'])
        step = timedelta(seconds=r['TS_step'])
        cur_date = start_date
        for v in r['DATAS']['nice']:
            yield mktime(cur_date.timetuple()), v
            cur_date += step
