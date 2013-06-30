from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from core.models import Host

from urllib2 import urlopen
from json import load as jload


class Storage(models.Model):
    name = models.CharField(_('name'), max_length=100, blank=True, null=True)
    address = models.CharField(_('address'), max_length=200)
    port = models.IntegerField(_('port'), blank=True,null=True,default=80)
    url_prefix = models.CharField(_('URL prefix'), max_length=100, blank=True, null=True)
    login = models.CharField(_('login'), max_length=100, blank=True, null=True)
    password = models.CharField(_('password'), max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'core'
        ordering = ('name',)
        verbose_name = _('storage')
        verbose_name_plural = _('storages')

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return self.address

    def __init__(self, *args, **kwargs):
        super(Storage, self).__init__(*args, **kwargs)
        self._set_proxy()
        self.urls = {
            'hosts': '/numeter-storage/hosts',
            'host': '/hinfo?host={storage_id}',
            'plugins': '/numeter-storage/list?host={storage_id}',
            'data': '/numeter-storage/data?host={storage_id}&plugin={plugin}&ds={ds}&res={res}',
        }

    def _set_proxy(self):
        """
        Set an URL opener for the current storage.
        """
        from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, build_opener, install_opener

        if self.login:
            passman = HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, self.address, self.login, self.password)
            authhandler = HTTPBasicAuthHandler(passman)
            self.proxy = build_opener(authhandler)
        else:
            self.proxy = build_opener()
        install_opener(self.proxy)

    def get_absolute_url(self):
        return reverse('core.views.user', args=[str(self.id)])

    def get_update_url(self):
        return reverse('core.views.user_update', args=[str(self.id)])

    def get_delete_url(self):
        return reverse('core.views.user_delete', args=[str(self.id)])

    def _connect(self, url, data={}):
        """Basic method for use proxy to storage."""
        if url not in self.urls:
            raise ValueError("URL key does not exists.")
        _url = urls[url].format(**data)
        r = self.proxy.open(_url, timeout=3)
        return jload(r)

    def get_hosts(self):
        """Return a dictionnary representing storage's hosts."""
        return self._connect('hosts')

    def get_info(self, storage_id):
        """Return a dictionnary representing an host on storage."""
        if isinstance(storage_id, Host): storage_id = storage_id.storage_id
        return self._connect('host', {'host_id': storage_id})

    def get_plugins(self):
        """Return a dictionnary representing an host's plugins."""
        # TODO : WTF on JSON
        r = self._connect('plugins', {'host_id': storage_id})
        for p in r['list'].values():
            yield jloads(p)

    def get_data(self, **data):
        return self._connect('data', **data)
        # TODO Add docs

    def _update_hosts(self):
        """
        Delete storage's hosts and create new.
        Be careful it won't remember groups.
        """
        Host.objects.filter(storage=self).delete()
        hosts = self.get_hosts().values()
        for h in hosts:
            Host.objects.create(
                name=h['Name'],
                host_id=h['ID'],
                storage=self,
            )
