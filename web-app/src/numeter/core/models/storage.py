from django.db import models
from core.models import Host
from urllib2 import urlopen
from json import load as jload


class Storage(models.Model):
    name = models.CharField(max_length=200)
    ip = models.IPAddressField()
    port = models.IntegerField(blank=True,null=True,default=80)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return self.ip

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
