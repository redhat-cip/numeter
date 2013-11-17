"""
Host management commands module.
"""

from django.core.management.base import BaseCommand, CommandError

from core.models import Storage, Host, Plugin
from configuration.forms.host import Host_Form
from core.management.commands._utils import CommandDispatcher
from core.management.commands.plugin import List_Command as Plugins_Command

from optparse import make_option
from os import devnull
import sys


class Command(CommandDispatcher):
    """Host management base command."""
    actions = ('list','add','delete','del','modify','mod','repair','plugins')

    def _subcommand_names(self):
        return ('list','add','delete','del','modify','mod','repair','plugins')

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
        elif args[0] == 'repair':
            return Repair_Command()
        elif args[0] == 'plugins':
            return Plugins_Command()


ROW_FORMAT = '{id:5} | {name:40} | {hostid:50} | {storage_id:10} | {group_id:9}'
class List_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-s', '--saved', action='store_true', default=False, help="Only list host saved in db"),
    )
    def handle(self, *args, **opts):
        self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'group_id': 'Group ID', 'hostid': 'Host ID', 'name': u'Name', 'storage_id': 'Storage ID'}))
        hosts = Storage.objects.get_all_host_info()
        for id,hinfo in Storage.objects.get_all_host_info().items():
            if Host.objects.filter(hostid=id).exists():
                h = Host.objects.get(hostid=id)
                self.stdout.write(ROW_FORMAT.format(**h.__dict__))
            elif not opts['saved']:
                s = Storage.objects.which_storage(id)
                h = {'id':'None', 'group_id':'None', 'hostid': id, 'name': hinfo['Name'], 'storage_id': s.id}
                self.stdout.write(ROW_FORMAT.format(**h))
        # Print count
        if not opts['saved']:
            self.stdout.write('Total count: %i' % len(hosts))
        self.stdout.write('Saved count: %i' % Host.objects.count())


class Add_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default=None, help="Select hosts by ID separated by comma"),
        make_option('-a', '--all', action='store_true', default=False, help="Add all host."),
        make_option('-g', '--group', action='store', default=None, help="Set group by ID."),
        make_option('-q', '--quiet', action='store_true', help="Don't print info."),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Create all if enabled
        if opts['all']:
            for s in Storage.objects.all():
                s.create_hosts()
                self.stdout.write('All host from %s created.' % s)
            return
        # Select host by id or ids
        if opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
        else:
            self.stdout.write("You must give one or more ID.")
            self.print_help('host', 'help')
            sys.exit(1)
        # Walk on ids to dispatch it on category
        non_saved_ids = []
        existing_ids = []
        non_existing_ids = []
        repaired_ids = []
        for id in ids:
            storage = Storage.objects.which_storage(id)
            if not storage:
                self.stdout.write('Host with ID %s not found in storage(s).' % id)
                non_existing_ids.append(id)
            # Repair and stop if already exists
            elif Host.objects.filter(hostid=id).exists():
                self.stdout.write('Host with ID %s already exists in db.' % id)
                h = Host.objects.get(hostid=id)
                if h.storage != storage:
                    self.stdout.write("%s wasn't linked to good storage, now linked to %s" % (id,storage))
                    h.storage = storage
                    h.save()
                    repaired_ids.append(id)
                else:
                    existing_ids.append(id)
            else:
                non_saved_ids.append(id)
        # Create hosts
        self.stdout.write('* Host creation:')
        self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'group_id': 'Group ID', 'hostid': 'Host ID', 'name': u'Name', 'storage_id': 'Storage ID'}))
        for id in non_saved_ids:
            host_info = storage.get_info(id)
            data = {
                'name': host_info['Name'],
                'hostid': id,
                'storage': storage.id,
                'group': opts['group']
            }
            # Use Form to valid
            F = Host_Form(data=data)
            if F.is_valid():
                h = F.save()
                self.stdout.write(ROW_FORMAT.format(**h.__dict__))
            else:
                self.stdout.write(h)
                for field,errors in F.errors.items():
                    self.stdout.write(field)
                    for err in errors:
                        self.stdout.write('\t'+err)
        # Show repaired hosts 
        if repaired_ids:
            self.stdout.write('* Hosts repaired:')
            for h in Host.objects.filter(hostid__in=repaired_ids): 
                self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'group_id': 'Group ID', 'hostid': 'Host ID', 'name': u'Name', 'storage_id': 'Storage ID'}))
                self.stdout.write(ROW_FORMAT.format(**h.__dict__))


class Delete_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default=None, help="Select hosts by ID separated by comma"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select host by id or ids
        if opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
            hosts = Host.objects.filter(hostid__in=ids)
        else:
            self.stdout.write("You must give one or more ID.")
            self.print_help('host', 'help')
            sys.exit(1)
        # Stop if no given id
        if not hosts.exists():
            self.stdout.write("There's no host with given ID: '%s'" % (opts['ids'] or opts['id']) )
            sys.exit(1)
        for h in hosts:
            h.delete()
            self.stdout.write('Delete host: %s' % h)


class Modify_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', help="Select hosts by ID separated by comma"),
        make_option('-s', '--storage', action='store', default=None, help="Set storage by id"),
        make_option('-g', '--group', action='store', default=None, help="Set group by id"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select host by id or ids
        ids = [ i.strip() for i in opts['ids'].split(',') ]
        hosts = Host.objects.filter(hostid__in=ids)
        # Stop if no given id
        if not hosts.exists():
            self.stdout.write("There's no host with given ID: '%s'" % (opts['ids'] or opts['id']) )
            sys.exit(1)

        existing_ids = [ h.hostid for h in hosts ]
        non_existing_ids = [ id for id in ids if id not in existing_ids ]
        modified_hosts = []
        form_error = None
        # Walk on host for valid or fail
        for h in hosts:
            # Make validation
            if not opts['storage']:
                opts['storage'] = h.storage.id
            if h.group and not opts['group']:
                opts['group'] = h.group.id
            # Create new data computing instance and options
            data = dict( [ (key.replace('_id', ''),val) for key,val in h.__dict__.items() if val is not None ] )
            data.update(opts)
            # Use Form to valid
            F = Host_Form(data=data, instance=h)
            if F.is_valid():
                h = F.save()
                modified_hosts.append(h)
            else:
                form_error = F.errors
        # Walk on all list to print it
        if modified_hosts:
            self.stdout.write('* Host updated:')
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'group_id': 'Group ID', 'hostid': 'Host ID', 'name': u'Name', 'storage_id': 'Storage ID'}))
            for h in modified_hosts:
                self.stdout.write(ROW_FORMAT.format(**h.__dict__))

        if non_existing_ids:
            self.stdout.write('* No host with following IDs:') 
            for id in non_existing_ids:
                self.stdout.write(id)
        if form_error:
            self.stdout.write('* Error:')
            for field,errors in form_error.items():
                self.stdout.write(field)
                for err in errors:
                    self.stdout.write('\t'+err)


class Repair_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        self.stdout.write('Repairing broken hosts.')
        Storage.objects.repair_hosts()
