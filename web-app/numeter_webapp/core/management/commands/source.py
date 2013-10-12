from django.core.management.base import BaseCommand, CommandError

from core.models import Host, Plugin, Data_Source as Source
from core.management.commands._utils import CommandDispatcher

from optparse import make_option
from os import devnull
import sys
import re


class Command(CommandDispatcher):
    """Storage management base command."""
    actions = ('list','add','delete','del')
    def _subcommand_names(self):
        return ('list','add','delete','del')

    def _subcommand(self, *args, **opts):
        """Dispatch in a Command by reading first argv."""
        if not args or args[0] not in self.actions:
            self.stdout.write(self.usage('host'))
        elif args[0] == 'list':
            return List_Command()
        elif args[0] == 'add':
            return Add_Command()
        elif args[0] in ('delete','del'):
            return Delete_Command()


ROW_FORMAT = '{id:5} | {name:35} | {plugin:25} | {host:30}'
class List_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default='', help="Select plugins by ID separated by comma"),
        make_option('-s', '--saved', action='store_true', default=False, help="Only list plugins saved in db"),
    )

    def handle(self, *args, **opts):
        # TODO: use this snippets for other
        # Select plugin by id or ids
        ids = [ i.strip() for i in opts['ids'].split(',') if i ]
        plugins = Plugin.objects.filter(id__in=ids) or Plugin.objects.all()
        # Walk on host and list plugins
        for p in plugins:
            self.stdout.write("* %s sources:" % p)
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'name': 'Name', 'plugin': 'Plugin', 'host': 'Host'}))
            # List plugins
            for s in p.get_data_sources():
                if Source.objects.filter(plugin=p, name=s).exists():
                    s = Source.objects.create(plugin=p, name=s).__dict__
                    s.update({'plugin': p.name, 'host': p.host.name})
                    self.stdout.write(ROW_FORMAT.format(**s))
                elif not opts['saved']:
                    s = {'plugin': p.name, 'host': p.host.name, 'name': s, 'id': 'None'}
                    self.stdout.write(ROW_FORMAT.format(**s))
            #self.stdout.write('Saved cound: %i' % sources


class Delete_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default=None, help="Select source by ID separated by comma"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select group by ids
        if opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
            sources = Source.objects.filter(id__in=ids)
        else:
            self.stdout.write("You must give one or more ID.")
            self.print_help('source', 'help')
            sys.exit(1)
        # Stop if no given id
        if not sources.exists():
            self.stdout.write("There's no source with given ID: '%s'" % opts['ids'] )
            sys.exit(1)
        for s in sources:
            s.delete()
            self.stdout.write('Delete source: %s' % s)
 
 
class Add_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', help="Select plugins by ID separated by comma"),
        make_option('-p', '--pattern', action='store', default='.*', help="Select sources by pattern"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        if opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
            plugins = Plugin.objects.filter(id__in=ids)
        else:
            plugins = Plugin.objects.all()
        # Skip if plugins don't exists
        if not plugins.exists():
            self.stdout.write("There's no plugin with given ID: '%s'" % opts['ids'] )
            sys.exit(1)

        # Walk on plugin and save matching sources
        REG_PLUGIN = re.compile(opts['pattern'])
        self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'name': 'Name', 'plugin': 'Plugin', 'host': 'Host'}))
        for p in plugins:
            sources = p.get_data_sources()
            for s in sources:
                if REG_PLUGIN.search(s) and not Source.objects.filter(name=s, plugin=p).exists():
                    s = Source.objects.create(name=s, plugin=p)
                    s_data = s.__dict__
                    s_data.update({'plugin': p.name, 'host': p.host})
                    self.stdout.write(ROW_FORMAT.format(**s_data))
