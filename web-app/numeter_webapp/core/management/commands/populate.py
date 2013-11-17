"""
Fast data insertion command module.
Populate all hosts, plugin and storage.
"""

from django.core.management.base import BaseCommand, CommandError

from core.models import Storage, Host, Plugin, Data_Source as Source

from optparse import make_option
import logging
import sys


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default=None, help="Select storage by id (by default select all)"),
        make_option('-H', '--host', action='store_true', help="Force to walk on already created hosts"),
        make_option('-P', '--plugin', action='store_true', help="Force to walk on already created plugins"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Walk on storage
        if opts['ids'] == 'all':
            storages = Storage.objects.all()
        elif opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
            storages = Storage.objects.filter(id__in=ids)
        else:
            self.stdout.write("Select a storage by id or 'all' for alm")
            return
            
        for s in storages:
            self.stdout.write('Creating hosts from storage %s' % s)
            hosts = s.create_hosts()
            hosts = hosts if not opts['host'] else Host.objects.filter(storage=s)
            # Walk on hosts
            for h in hosts:
                self.stdout.write('Creating plugins from host %s' % h)
                plugins = h.create_plugins()
                plugins = plugins if not opts['plugin'] else Plugin.objects.filter(host=h)
                # Walk on plugins
                for p in plugins:
                    self.stdout.write('Creating sources from plugin %s' % p)
                    p.create_data_sources()
        self.stdout.write('Done.')
        self.stdout.write('%i host(s)' % Host.objects.count())
        self.stdout.write('%i plugin(s)' % Plugin.objects.count())
        self.stdout.write('%i source(s)' % Source.objects.count())
