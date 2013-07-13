from django.db import models
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
