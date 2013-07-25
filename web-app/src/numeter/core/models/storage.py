from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from core.models import Host

from urllib2 import urlopen
from urllib import quote
from json import load as jload, loads as jloads
import socket
from logging import getLogger
logger = getLogger(__name__)


class Storage_Manager(models.Manager):

    def get_all_host_info(self):
        """Return a list of all hosts' datas."""
        host_list = []
        for S in Storage.objects.all():
            host_list.extend(S.get_hosts())
        return host_list

    def get_all_hostids(self):
        """Return a list of ids of all hosts from storage."""
        return [ h['ID'] for h in self.get_all_host_info() ]

    def get_unfoundable_hostids(self):
        """
        Return a list of ids of all unfoundable hosts.
        Those hosts can be in wrong storage.
        """
        host_list = []
        for S in self.get_query_set():
            host_list.extend(S._get_unfoundable_hostids())
        return host_list

    def get_bad_referenced_hostids(self):
        """Return a list of ids of hosts which are saved in wrong storage."""
        host_list = []
        # Get all unfoundable
        for h in self.get_unfoundable_hostids():
            # Retain only which are saved in a storage
            if Host.objects.filter(hostid=h).exists():
                host_list.append(h)
        return host_list

    def get_unsaved_hostids(self):
        """Return a list of hosts which aren't saved."""
        host_list = []
        for S in self.get_query_set():
            host_list.extend(S._get_unsaved_hosts())
        return host_list

    def get_host(self, hostid):
        """Search an hostid on all storage."""
        host_list = self.get_all_hostids()
        try:
            hostid = [ h for h in host_list if h == hostid ][0]
        except IndexError:
            raise ValueError("Bad host ID.")
        return Host.objects.get(hostid=hostid)

    def get_hosts(self, hostids):
        """Search a list of hostid on all storage."""
        host_list = self.get_all_hostids()
        return Host.objects.filter(hostid__in=hostids)

    def which_storage(self, hostid):
        """Return the storage of owner of an hostid."""
        for s in self.get_query_set():
            hosts = s._get_hostids()
            for h in hosts:
                if h == hostid:
                    return s
        return

    def repair_hosts(self):
        for h in self.get_bad_referenced_hostids():
            whereishost = self.which_storage(h)
            if whereishost is not None:
                Host.objects.filter(hostid=h).update(storage=whereishost)


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

    objects = Storage_Manager()
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
        return reverse('storage', args=[str(self.id)])

    def get_add_url(self):
        return reverse('storage add')

    def get_list_url(self):
        return reverse('storage list')

    def get_update_url(self):
        if not self.id:
            return self.get_add_url()
        return reverse('storage update', args=[str(self.id)])

    def get_delete_url(self):
        return reverse('storage delete', args=[str(self.id)])

    def get_create_hosts_url(self):
        return reverse('storage create hosts', args=[str(self.id)])

    def get_external_url(self):
        return "%(protocol)s://%(address)s:%(port)i%(url_prefix)s" % self.__dict__

    def _connect(self, url, data={}):
        """Basic method for use proxy to storage."""
        if url not in self.urls:
            raise ValueError("URL key does not exists.")

        data['res'] = data.get('res','Daily')
        if 'plugin' in data:
            data['plugin'] = quote(data['plugin'])

        _url = self.urls[url].format(**data)
        uri = ("%(protocol)s://%(address)s:%(port)i%(url_prefix)s" % self.__dict__) + _url
        print uri
        logger.info('STORAGE-GET %s' % uri)
        r = self.proxy.open(uri, timeout=settings.STORAGE_TIMEOUT).read()
        return jloads(r)

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

    def get_plugin_data_sources(self, hostid, plugin):
        for p in self.get_plugins(hostid):
            if p['Plugin'].lower() == plugin.lower():
                return p['Infos'].keys()

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

    def _get_hostids(self):
        """Return a list of host's from storage."""
        hosts = self.get_hosts().values()
        return [ h['ID'] for h in hosts ]

    def _get_unsaved_hosts(self):
        """Lookup up for hosts foundable on this storage but not in db."""
        saved_hosts = [ H.hostid for H in Host.objects.filter(storage=self) ]
        remote_hosts = self._get_hostids()
        diff = set(saved_hosts) ^ set(remote_hosts)
        unsaved = list( set(remote_hosts) & diff )
        return unsaved

    def _get_unfoundable_hostids(self):
        """Lookup up for hosts saved in db but unfoundable on this storage."""
        saved_hosts = [ H.hostid for H in Host.objects.filter(storage=self) ]
        remote_hosts = self._get_hostids()
        diff = set(saved_hosts) ^ set(remote_hosts)
        unfoundable = list( set(saved_hosts) & diff )
        return unfoundable

    def _simple_create_hosts(self):
        """Create hosts in db if it doesn't already exist."""
        hosts = self.get_hosts().values()
        for h in hosts:
            if not Host.object.filter(hostid=h['ID']).exists():
                Host.objects.create(
                    name=h['Name'],
                    hostid=h['ID'],
                    storage=self,
                )

    def create_hosts(self):
        """Create hosts and update aleardy existing."""
        hosts = self.get_hosts().values()
        for h in hosts:
            if not Host.objects.filter(hostid=h['ID']).exists():
                Host.objects.create(
                    name=h['Name'],
                    hostid=h['ID'],
                    storage=self,
                )
            else:
                Host.objects.filter(hostid=h['ID']).update(storage=self)

