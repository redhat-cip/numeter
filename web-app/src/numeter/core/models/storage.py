from django.db import models
from core.models import Host
from urllib2 import urlopen
from json import load as jload


class Storage(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200)
    port = models.IntegerField(blank=True,null=True,default=80)
    url_prefix = models.CharField(max_length=100, blank=True, null=True)
    login = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return self.address

    def __init__(self, *args, **kwargs):
        super(Storage, self).__init__(*args, **kwargs)
        # TODO : Add opener snipets
        # self.proxy = ...

    def get_hosts(self):
        f = urlopen('http://%s:%s/numeter-storage/hosts' % (self.ip,self.port))
        return jload(f)

    def update_hosts(self):
        Host.objects.filter(storage=self).delete()
        hosts = self.get_hosts().values()
        for h in hosts:
            Host.objects.create(
                name=h['Name'],
                host_id=h['ID'],
                storage=self,
            )
