from django.core.management.base import BaseCommand, CommandError

from core.models import Host, Plugin
from configuration.forms.plugin import Plugin_Form
from core.management.commands._utils import CommandDispatcher

from optparse import make_option
from os import devnull
import sys
import re


class Command(CommandDispatcher):
    """Storage management base command."""
    actions = ('list','add','delete','del','modify','mod','hosts')
    def _subcommand_names(self):
        return ('list','add','delete','del','modify','mod','hosts')

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
        elif args[0] in ('modify','mod'):
            return Modify_Command()
        elif args[0] == 'hosts':
            return Hosts_Command()


ROW_FORMAT = '{id:5} | {name:40} | {hostid:50}'
class List_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default=None, help="Select hosts by ID separated by comma"),
        make_option('-s', '--saved', action='store_true', default=False, help="Only list plugins saved in db"),
    )

    def handle(self, *args, **opts):
        # Select host by id or ids
        if opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
            hosts = Host.objects.filter(hostid__in=ids)
        else:
            hosts = Host.objects.all()
        # Stop if no given id
        if not hosts.exists():
            self.stdout.write("There's no host with given ID: '%s'" % (opts['ids'] or opts['id']) )
            sys.exit(1)
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
        make_option('-i', '--ids', action='store', default=None, help="Select hosts by ID separated by comma"),
        make_option('-p', '--pattern', action='store', default='.*', help="Select by pattern"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        hosts = Host.objects.filter(hostid=opts['ids'])
        # Skip if hosts don't exists
        if not hosts.exists():
            self.stdout.write("There's no host with given ID: '%s'" % opts['ids'] )
            sys.exit(1)

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
# 
# 
# class Modify_Command(BaseCommand):
#     option_list = BaseCommand.option_list + (
#         make_option('-i', '--ids', action='store', help="Select storages by IDs separated by comma"),
#         make_option('-n', '--name', action='store', default=None, help="Set name"),
#         make_option('-a', '--address', action='store', default=None, help="Set IP or FQDN"),
#         make_option('-p', '--port', action='store', default=None, help="Set port"),
#         make_option('-u', '--url_prefix', action='store', default=None, help="Set url prefix"),
#         make_option('-P', '--protocol', action='store', default=None, help="Set HTTP or HTTPS"),
#         make_option('-l', '--login', action='store', default=None, help="Set HTTP login"),
#         make_option('-w', '--password', action='store', default=None, help="Set HTTP password"),
#         make_option('-q', '--quiet', action='store_true', help="Don't print info"),
#     )
# 
#     def handle(self, *args, **opts):
#         if opts['quiet']: self.stdout = open(devnull, 'w')
#         # Select storage by id
#         ids = [ i.strip() for i in opts['ids'].split(',') ]
#         storages = Storage.objects.filter(id__in=ids)
#         if not storages.exists():
#             self.stdout.write("No storage with id '%s' exists." % opts['id'])
#             sys.exit(1)
#         existing_ids = [ s.id for s in storages ]
#         non_existing_ids = [ id for id in ids if int(id) not in existing_ids ]
#         modified_storages = []
#         form_error = None
#         # Format options to left 'None'
#         opts = dict([ (k,v) for k,v in opts.items() if v is not None ])
#         # Walk on host for valid or fail
#         for s in storages:
#             # Make validation
#             # Create new data computing instance and options
#             data = dict( [ (key.replace('_id', ''),val) for key,val in s.__dict__.items() ] )
#             data.update(opts)
#             # Use Form to valid
#             F = Storage_Form(data=data, instance=s)
#             if F.is_valid():
#                 h = F.save()
#                 modified_storages.append(s)
#             else:
#                 form_error = F.errors
# 
#         # Walk on all list to print it
#         if modified_storages:
#             self.stdout.write('* Storage(s) updated:')
#             self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'name': 'Name', 'address': 'Address', 'port': 'Port', 'url_prefix': 'URL prefix', 'protocol': 'Protocol', 'login': 'Login'}))
#             for s in modified_storages:
#                 self.stdout.write(ROW_FORMAT.format(**s.__dict__))
# 
#         if non_existing_ids:
#             self.stdout.write('* No storage with following IDs:') 
#             for id in non_existing_ids:
#                 self.stdout.write(id)
#         if form_error:
#             self.stdout.write('* Error:')
#             for field,errors in form_error.items():
#                 self.stdout.write(field)
#                 for err in errors:
#                     self.stdout.write('\t'+err)
