from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.cache import cache

from core.models import Host

from urllib2 import urlopen
from urllib import quote
from json import load as jload, loads as jloads
import socket
from hashlib import md5
from logging import getLogger
logger = getLogger('storage')


RESOLUTION_STEP = { # in minute
  'Daily': 60, # Hour
  'Weekly': 720, # Half-day 
  'Monthly': 1140, # Day
  'Yearly': 17100 # Half-month
}

class Storage_Manager(models.Manager):
    """Custom Manager with extra methods."""
    def web_filter(self, q):
        return self.filter(
            Q(name__icontains=q) |
            Q(address__icontains=q)
        ).distinct()

    def get_all_host_info(self):
        """Return a list of all hosts' infos."""
        host_dict = {}
        for S in Storage.objects.all():
            try:
                host_dict.update(S.get_hosts())
            except Storage.ConnectionError:
                pass
        return host_dict

    def get_all_hostids(self):
        """Return a list of ids of all hosts from storage."""
        return [ h['ID'] for h in self.get_all_host_info().values() ]

    def get_unfoundable_hostids(self):
        """
        Return a list of ids of all unfoundable hosts.
        Those hosts can be in wrong storage.
        """
        host_list = []
        for S in self.get_query_set():
            try:
                host_list.extend(S._get_unfoundable_hostids())
            except Storage.ConnectionError:
                pass
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

    # TODO
    def get_hosts(self, hostids):
        """Search a list of hostid on all storage."""
        return self.get_all_hostids()

    def which_storage(self, hostid):
        """Return the storage of owner of an hostid."""
        # TODO: Remake with better meth
        for s in self.get_query_set():
            try:
                hosts = s.get_hosts()
                for h in hosts:
                    if h == hostid:
                        return s
            except Storage.ConnectionError:
                pass
        return

    def repair_hosts(self):
        """Try to repair all storage/host links."""
        for h in self.get_bad_referenced_hostids():
            whereishost = self.which_storage(h)
            if whereishost is not None:
                Host.objects.filter(hostid=h).update(storage=whereishost)


class Storage(models.Model):
    """
    Corresponding to a storage.
    Attributes are needed informations for connect to storage's API.
    """
    HTTP_PROTOCOLS = (
      ('http','HTTP'),
      ('https','HTTPS'),
    )

    name = models.CharField(_('name'), max_length=100, blank=True, null=True)
    address = models.CharField(_('address'), max_length=200)
    port = models.IntegerField(_('port'), blank=True, null=True, default=80)
    url_prefix = models.CharField(_('URL prefix'), max_length=100, default='', blank=True, help_text=_('Start point of API'))
    protocol = models.CharField(_('protocol'), max_length=5, default='HTTP', choices=HTTP_PROTOCOLS)
    login = models.CharField(_('login'), max_length=100, blank=True, null=True, help_text=('Used for HTTP authentification'))
    password = models.CharField(_('password'), max_length=100, blank=True, null=True)

    objects = Storage_Manager()
    class Meta:
        app_label = 'core'
        ordering = ('name',)
        verbose_name = _('storage')
        verbose_name_plural = _('storages')

    class ConnectionError(Exception):
        "Can't connect to storage"
        pass

    class UnvalidDataError(Exception):
        "Can't read data from storage"
        pass

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return self.address

    def __init__(self, *args, **kwargs):
        super(Storage, self).__init__(*args, **kwargs)
        self._set_proxy()
        self.URLS = {
            'hosts': '/hosts',
            'host': '/hinfo?host={hostid}',
            'plugins': '/list?host={hostid}',
            'data': '/data?host={hostid}&plugin={plugin}&ds={ds}&res={res}',
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
        """Test if storage is reachable"""
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
        return reverse('storage-create-hosts', args=[str(self.id)])

    def get_rest_list_url(self):
       return reverse('storage-list') 

    def get_rest_detail_url(self):
       return reverse('storage-detail', args=[self.id]) 

    def get_external_url(self):
        """Return the storage's API url."""
        return "%(protocol)s://%(address)s:%(port)i%(url_prefix)s" % self.__dict__

    def _connect(self, url, data={}):
        """
        Basic method for use proxy to storage.
        `data` should be as following:
         - host: requested host id on storage
         - plugin: requested plugin name
         - ds: requested data sources separated by ','
         - res: resolution by default Daily
        """
        if url not in self.URLS:
            raise ValueError("URL key does not exists.")

        data['res'] = data.get('res','Daily')
        if 'plugin' in data:
            data['plugin'] = quote(data['plugin'])

        _url = self.URLS[url].format(**data)
        uri = ("%(protocol)s://%(address)s:%(port)i%(url_prefix)s" % self.__dict__) + _url
        logger.info(uri)
        try:
            r = self.proxy.open(uri, timeout=settings.STORAGE_TIMEOUT).read()
        except IOError, e:
            raise self.ConnectionError(e)
        return jloads(r)

    def create_host(self, hostid):
        """Create a host in DB from its storage ID."""
        hosts = self.get_hosts()
        h = hosts[hostid]
        h = Host.objects.create(
            name=h['Name'],
            hostid=h['ID'],
            storage=self,
        )
        return h

    def create_hosts(self, hostids=[], commit=True):
        """
        Create hosts from the given host ID list.
        If no host ID is given, all are created.
        """
        new_hosts = []
        for hostid,infos in self.get_hosts().items():
            if hostid in hostids or hostids == []:
                if not Host.objects.filter(hostid=hostid).exists():
                    new_hosts.append(Host(
                        name=infos['Name'],
                        hostid=infos['ID'],
                        storage=self,
                    ))
                else:
                    Host.objects.filter(hostid=hostid).update(storage=self)

        if commit:
            [ h.save() for h in new_hosts ]
        return new_hosts

    def get_hosts(self):
        """
        Return a dictionnary representing storage's hosts.
        It is raw data from storage API.
        """
        key_hash = md5( ('storage/%i-%s:%s/hosts' % (self.id, self.address, self.port)) ).hexdigest()
        data = cache.get(key_hash)
        if not data:
            data = self._connect('hosts')
            cache.set(key_hash, data)
        return data

    def get_info(self, hostid):
        """
        Return a dictionnary representing an host on storage.
        It is raw data from storage API.
        """
        if isinstance(hostid, Host): hostid = hostid.hostid
        key_hash = md5( ('storage/%i/hinfo/%s' % (self.id, hostid) ) ).hexdigest()
        data = cache.get(key_hash)
        if not data:
            data = self._connect('host', {'hostid': hostid})
            cache.set(key_hash, data)
        return data

    def get_plugins_raw(self, hostid):
        """
        Return a dict representing an host plugins' category.
        It is raw data from storage API.
        """
        key_hash = md5( ('storage/%i/plugins/%s' % (self.id, hostid) ) ).hexdigest()
        data = cache.get(key_hash)
        if not data:
            data = self._connect('plugins', {'hostid': hostid})
            cache.set(key_hash, data)
        return data

    def get_categories(self, hostid):
        """Return a list representing an host plugins' category."""
        r = self.get_plugins_raw(hostid)
        categories = set([ p['Category']  for p in r.values() ])
        return list(categories)

    def get_plugins(self, hostid):
        """
        Return a list representing an host's plugins.
        Modify storage's data before returning.
        """
        r = self.get_plugins_raw(hostid)
        return [ p for p in r.values() ]

    def get_plugins_by_category(self, hostid, category):
        """Get host's plugins by category."""
        return [ p for p in self.get_plugins(hostid) if p['Category'] == category ] 

    def get_plugin_data_sources(self, hostid, plugin):
        """Return a list of data sources of a plugin."""
        for p in self.get_plugins(hostid):
            if p['Plugin'].lower() == plugin.lower():
                return p['Infos'].keys()
        return []

    def get_data(self, **data):
        """
        Get plugin's data from storage.
        It is raw data from storage API.
        """
        key_hash = md5( ('storage/%i/data/%s/%s/%s/%s' % (self.id, data['hostid'], data['plugin'], data['ds'], data.get('res','Daily')) ) ).hexdigest()
        _data = cache.get(key_hash)
        if not _data:
            _data =  self._connect('data', data)
            cache.set(key_hash, _data )
        return _data

    def _get_unsaved_hosts(self):
        """Lookup up for hosts foundable on this storage but not in db."""
        saved_hosts = [ H.hostid for H in Host.objects.filter(storage=self) ]
        remote_hosts = self.get_hosts()
        diff = set(saved_hosts) ^ set(remote_hosts)
        unsaved = list( set(remote_hosts) & diff )
        return unsaved

    def _get_unfoundable_hostids(self):
        """Lookup up for hosts saved in db but unfoundable on this storage."""
        saved_hosts = [ H.hostid for H in Host.objects.filter(storage=self) ]
        remote_hosts = self.get_hosts()
        diff = set(saved_hosts) ^ set(remote_hosts)
        unfoundable = list( set(saved_hosts) & diff )
        return unfoundable
