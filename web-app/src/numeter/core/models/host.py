from django.db import models
from django.contrib.auth.models import Group, Permission
from django.utils.translation import ugettext_lazy as _


class Host(models.Model):
    """
    Corresponding to an hos on storage.
    """
    name = models.CharField(_('name'), max_length=200)
    hostid = models.CharField(_('ID on storage'), max_length=300)
    storage = models.ForeignKey('Storage')
    group = models.ForeignKey(Group, null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ('group','name','hostid')
        verbose_name = _('host')
        verbose_name_plural = _('hosts')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('host', args=[str(self.id)])

    def get_update_url(self):
        return reverse('update host', args=[str(self.id)])

    def get_delete_url(self):
        return reverse('delete host', args=[str(self.id)])

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
        return self.storage.get_plugins_by_category(self.hostid, category)
