from django.core.management.base import BaseCommand, CommandError

from core.models import Storage, Host
from configuration.forms.host import Host_Form
from core.management.commands._utils import CommandDispatcher

from optparse import make_option
from os import devnull
import sys


class Command(CommandDispatcher):
    """Host management base command."""
    actions = ('list','add','delete','del','modify','mod')

    def _subcommand_names(self):
        return ('list','add','delete','del','modify','mod')

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


ROW_FORMAT = '{id:5} | {name:40} | {hostid:50} | {storage_id:10} | {group_id:9}'
class List_Command(BaseCommand):
    def handle(self, *args, **opts):
        hosts = Host.objects.values()
        self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'group_id': 'Group ID', 'hostid': 'Host ID', 'name': u'Name', 'storage_id': 'Storage ID'}))
        for h in hosts:
            self.stdout.write(ROW_FORMAT.format(**h))
        self.stdout.write('Count: %i' % len(hosts))


class Add_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--id', action='store', default=None, help="Select host by ID"),
        make_option('-I', '--ids', action='store', default=None, help="Select hosts by ID separated by comma"),
        make_option('-a', '--all', action='store_true', default=False, help="Add all host."),
        make_option('-g', '--group', action='store', default=None, help="Set group by ID."),
        make_option('-q', '--quiet', action='store_true', help="Set group by ID."),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Create all if enabled
        if opts['all']:
            for s in Storage.objects.all():
                s.create_hosts()
                self.stdout.write('All host from %s create.' % s)
            sys.exit(1)

        # Select host by id or idss
        if opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
        elif opts['id']:
            ids = [ opts['id'] ]
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
        make_option('-i', '--id', action='store', default=None, help="Select host by ID"),
        make_option('-I', '--ids', action='store', default=None, help="Select hosts by ID separated by comma"),
        make_option('-q', '--quiet', action='store_true', help="Set group by ID."),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select host by id or idss
        if opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
            hosts = Host.objects.filter(hostid__in=ids)
        elif opts['id']:
            hosts = Host.objects.filter(hostid=opts['id'])
        else:
            self.stdout.write("You must give one or more ID.")
            self.print_help('host', 'help')
            sys.exit(1)
        # Stop if no given id
        if not hosts.exists():
            self.stdout.write("There's no Host with given ID: '%s'" % (opts['ids'] or opts['id']) )
            sys.exit(1)
        for h in hosts:
            h.delete()
            self.stdout.write('Delete host: %s' % h)


class Modify_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--id', action='store', default=None, help="Select host by ID"),
        make_option('-s', '--storage', action='store', help="Set storage by id"),
        make_option('-g', '--group', action='store', help="Set group by id"),
        make_option('-q', '--quiet', action='store_true', help="Set group by ID."),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Stop if doesn't exist
        if not Host.objects.filter(hostid=opts['id']):
            self.stdout.write("Host doesn't exist")
            sys.exit(1)
        host = Host.objects.get(hostid=opts['id'])
        # Make validation
        if not opts['storage']:
            opts['storage'] = host.storage.id
        if host.group and not opts['group']:
            opts['group'] = host.group.id
        # Create new data computing instance and options
        data = dict( [ (key.replace('_id', ''),val) for key,val in host.__dict__.items() ] )
        data.update(opts)
        # Use Form to valid
        F = Host_Form(data=data, instance=host)
        if F.is_valid():
            host = F.save()
            self.stdout.write('Host updated.')
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'group_id': 'Group ID', 'hostid': 'Host ID', 'name': u'Name', 'storage_id': 'Storage ID'}))
            self.stdout.write(ROW_FORMAT.format(**host.__dict__))
        else:
            for field,errors in F.errors.items():
                self.stdout.write(field)
                for err in errors:
                    self.stdout.write('\t'+err)
