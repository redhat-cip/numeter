from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from core.models import Host

from urllib2 import urlopen
from json import load as jload, loads as jloads
import socket
from logging import getLogger
logger = getLogger(__name__)


class Storage(models.Model):
    """
    Corresponding to a storage.
    """
    HTTP_PROTOCOLS = (
      ('http','HTTP'),
      ('https','HTTPS'),
    )

    name = models.CharField(_('name'), max_length=100, blank=True, null=True)
    address = models.CharField(_('address'), max_length=200)
    port = models.IntegerField(_('port'), blank=True,null=True,default=80)
    url_prefix = models.CharField(_('URL prefix'), max_length=100, blank=True, null=True)
    protocol = models.CharField(_('protocol'), max_length=5, default='http', choices=HTTP_PROTOCOLS)
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
            'host': '/numeter-storage/hinfo?host={hostid}',
            'plugins': '/numeter-storage/list?host={hostid}',
            'data': '/numeter-storage/data?host={hostid}&plugin={plugin}&ds={ds}&res={res}',
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

    def is_on(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.address, self.port))
            s.close()
            return True
        except socket.error as msg:
            return False

    def get_absolute_url(self):
        return reverse('storage index', args=[str(self.id)])

    def get_add_url(self):
        return reverse('storage add')

    def get_update_url(self):
        if not self.id:
            return self.get_add_url()
        return reverse('storage update', args=[str(self.id)])

    def get_delete_url(self):
        return reverse('storage delete', args=[str(self.id)])

    def _connect(self, url, data={}):
        """Basic method for use proxy to storage."""
        if url not in self.urls:
            raise ValueError("URL key does not exists.")
        _url = self.urls[url].format(**data)
        uri = "http://%s:%i%s" % (self.address, self.port, _url)
        logger.info('STORAGE-GET %s' % uri)
        r = self.proxy.open(uri, timeout=settings.STORAGE_TIMEOUT)
        return jload(r)

    def create_host(self, hostid):
        hosts = self.get_hosts()
        h = hosts[hostid]
        Host.objects.create(
            name=h['Name'],
            hostid=h['ID'],
            storage=self,
        )

    def get_hosts(self):
        """Return a dictionnary representing storage's hosts."""
        return self._connect('hosts')

    def get_info(self, hostid):
        """Return a dictionnary representing an host on storage."""
        if isinstance(hostid, Host): hostid = hostid.hostid
        return self._connect('host', {'hostid': hostid})

    def get_categories(self, hostid):
        """Return a list representing an host plugins' category."""
        r = self._connect('plugins', {'hostid': hostid})
        categories = set([ p['Category']  for p in r.values() ])
        return list(categories)

    def get_plugins(self, hostid):
        """Return a dictionnary representing an host's plugins."""
        # TODO : WTF on JSON
        r = self._connect('plugins', {'hostid': hostid})
        for p in r.values():
            yield p

    def get_plugins_by_category(self, hostid, category):
        return [ p for p in self.get_plugins(hostid) if p['Category'] == category ] 

    def get_data(self, **data):
        return self._connect('data', data)
        # TODO Add docs

    def _update_hosts(self):
        """
        Delete storage's hosts and create new.
        Be careful it won't remember groups.
        """
        Host.objects.filter(storage=self).delete()
        # TODO : test this part
        # hostids = self.get_hosts().keys()
        # for hostid in hostids:
        #     self.create_host(hostid)
        hosts = self.get_hosts().values()
        for h in hosts:
            Host.objects.create(
                name=h['Name'],
                hostid=h['ID'],
                storage=self,
            )
