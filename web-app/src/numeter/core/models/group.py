from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class Group(models.Model):
    name = models.CharField(_('name'), max_length=80, unique=True)

    class Meta:
        app_label = 'core'
        ordering = ('name',)
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('group', args=[self.id])

    def get_add_url(self):
        return reverse('group add')

    def get_update_url(self):
        if not self.id:
            return self.get_add_url()
        return reverse('group update', args=[str(self.id)])

    def get_delete_url(self):
        return reverse('group delete', args=[str(self.id)])

    def get_list_url(self):
        return reverse('group list')
