"""
Plugin management commands module.
"""

from django.core.management.base import BaseCommand, CommandError

from core.models import Host, Plugin
from configuration.forms.plugin import Plugin_Form
from core.management.commands._utils import CommandDispatcher
from core.management.commands.source import List_Command as Sources_Command

from optparse import make_option
from os import devnull
import sys
import re


class Command(CommandDispatcher):
    """Plugin management base command."""
    actions = ('list','add','delete','del','sources')
    def _subcommand_names(self):
        return ('list','add','delete','del','sources')

    def _subcommand(self, *args, **opts):
        """Dispatch in a Command by reading first argv."""
        if not args or args[0] not in self.actions:
            return self
        elif args[0] == 'list':
            return List_Command()
        elif args[0] == 'add':
            return Add_Command()
        elif args[0] in ('delete','del'):
            return Delete_Command()
        elif args[0] == 'sources':
            return Sources_Command()


ROW_FORMAT = '{id:5} | {name:40} | {hostid:50}'
class List_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default='', help="Select hosts by ID separated by comma"),
        make_option('-s', '--saved', action='store_true', default=False, help="Only list plugins saved in db"),
    )

    def handle(self, *args, **opts):
        # Select host by id or ids
        ids = [ i.strip() for i in opts['ids'].split(',') ]
        hosts = Host.objects.filter(hostid__in=ids)
        hosts = hosts if hosts.exists() else Host.objects.all()
        # Walk on host and list plugins
        for h in hosts:
            self.stdout.write("* %s plugins:" % h)
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'name': 'Name', 'hostid': 'Host ID'}))
            # List plugins
            for p in h.get_plugins():
                if Plugin.objects.filter(host=h, name=p['Plugin']).exists():
                    p = Plugin.objects.get(host=h, name=p['Plugin']).__dict__
                    p['hostid'] = h.hostid
                    self.stdout.write(ROW_FORMAT.format(**p))
                elif not opts['saved']:
                    p = {'id': 'None', 'name': p['Plugin'], 'hostid': h.hostid}
                    self.stdout.write(ROW_FORMAT.format(**p))


class Delete_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default=None, help="Select plugin by ID separated by comma"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select group by ids
        if opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
            plugins = Plugin.objects.filter(id__in=ids)
        else:
            self.stdout.write("You must give one or more ID.")
            self.print_help('plugin', 'help')
            sys.exit(1)
        # Stop if no given id
        if not plugins.exists():
            self.stdout.write("There's no plugin with given ID: '%s'" % opts['ids'] )
            sys.exit(1)
        for p in plugins:
            p.delete()
            self.stdout.write('Delete plugin: %s' % p)
 
 
class Add_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', help="Select hosts by ID separated by comma"),
        make_option('-p', '--pattern', action='store', default='.*', help="Select plugins by pattern"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        hosts = Host.objects.filter(hostid=opts['ids'])
        # Skip if hosts don't exists
        if not hosts.exists():
            raise CommandError("There's no host with given ID: '%s'" % opts['ids'] )

        # Walk on host and save matching plugins
        REG_PLUGIN = re.compile(opts['pattern'])
        self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'name': 'Name', 'hostid': 'Host ID'}))
        for h in hosts:
            plugins = h.get_plugin_list()
            for p in plugins:
                if REG_PLUGIN.search(p) and not Plugin.objects.filter(name=p, host=h).exists():
                    p = Plugin.objects.create(name=p, host=h)
                    p_data = p.__dict__
                    p_data['hostid'] = h.hostid
                    self.stdout.write(ROW_FORMAT.format(**p_data))
