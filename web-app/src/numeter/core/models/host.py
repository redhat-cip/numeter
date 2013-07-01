from django.db import models
from django.contrib.auth.models import Group, Permission
from django.utils.translation import ugettext_lazy as _

from urllib2 import urlopen
from json import load as jload, loads as jloads, dumps as jdumps


class Host_QuerySet(models.query.QuerySet):
    def get_hosts_by_group(self):
        groups = list(set([ Group.objects.get(pk=g[0]) for g in self.values_list('group') ]))
        for group in groups:
            yield self.filter(id=group.id)

    # USELESS
    def get_list_tree(self):
        data = []
        groups = list(set([ Group.objects.get(pk=g[0]) for g in self.values_list('group') ]))
        for group in groups:
            branch = {'key':group.name}
            hosts = self.filter(id=group.id)
            branch['values'] = [ {'key':host.name} for host in hosts ]
            data.append(branch)
        return jdumps(data)


class Host_Manager(models.Manager):
    def get_query_set(self):
        return Host_QuerySet(self.model)


class Host(models.Model):
    name = models.CharField(_('name'), max_length=200)
    hostid = models.CharField(_('ID on storage'), max_length=300)
    storage = models.ForeignKey('Storage')
    group = models.ForeignKey(Group, null=True, blank=True)

    objects = Host_Manager()
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
        return self.storage.get_info(self.hostid)

    def get_plugins(self):
        return self.storage.get_plugins(self.hostid)
