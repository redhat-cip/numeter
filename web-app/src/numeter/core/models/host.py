from django.db import models
from django.contrib.auth.models import Group, Permission
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
    name = models.CharField(max_length=200)
    host_id = models.CharField(max_length=300)
    storage = models.ForeignKey('Storage')
    group = models.ForeignKey(Group, null=True, blank=True)

    objects = Host_Manager()
    class Meta:
        app_label = 'core'
        ordering = ('group','name','host_id')

    def __unicode__(self):
        return self.name

    def get_info(self):
        f = urlopen('http://%s:%s/numeter-storage/hinfo?host=%s' % (self.storage.ip,self.storage.port,self.host_id))
        return jload(f)

    # TODO : format storage
    def get_plugins(self):
        f = urlopen('http://%s:%s/numeter-storage/list?host=%s' % (self.storage.ip,self.storage.port,self.host_id))
        for p in jload(f)['list'].values():
            yield jloads(p)
        

