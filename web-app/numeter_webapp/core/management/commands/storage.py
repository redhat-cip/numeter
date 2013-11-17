"""
Storage management commands module.
"""

from django.core.management.base import BaseCommand, CommandError

from core.models import Storage
from configuration.forms.storage import Storage_Form
from core.management.commands._utils import CommandDispatcher
from core.management.commands.host import List_Command as Hosts_Command

from optparse import make_option
from os import devnull
import sys


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


ROW_FORMAT = '{id:5} | {name:30} | {address:30} | {port:5} | {url_prefix:30} | {protocol:8} | {login:15}'
class List_Command(BaseCommand):
    def handle(self, *args, **opts):
        storages = Storage.objects.values()
        self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'name': 'Name', 'address': 'Address', 'port': 'Port', 'url_prefix': 'URL prefix', 'protocol': 'Protocol', 'login': 'Login'}))
        for s in storages:
            self.stdout.write(ROW_FORMAT.format(**s))
        self.stdout.write('Count: %i' % len(storages))


class Delete_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default=None, help="Select storage by ID separated by comma"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select group by ids
        if opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
            storages = Storage.objects.filter(id__in=ids)
        else:
            self.stdout.write("You must give one or more ID.")
            self.print_help('storage', 'help')
            sys.exit(1)
        # Stop if no given id
        if not storages.exists():
            self.stdout.write("There's no storage with given ID: '%s'" % opts['ids'] )
            sys.exit(1)
        for s in storages:
            s.delete()
            self.stdout.write('Delete storage: %s' % s)
 
 
class Add_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-n', '--name', action='store', help="Set name"),
        make_option('-a', '--address', action='store', help="Set IP or FQDN"),
        make_option('-p', '--port', action='store', default=8080, help="Set port"),
        make_option('-u', '--url_prefix', action='store', default='', help="Set url prefix"),
        make_option('-P', '--protocol', action='store', default='http', help="Set HTTP or HTTPS"),
        make_option('-l', '--login', action='store', default='', help="Set HTTP login"),
        make_option('-w', '--password', action='store', default='', help="Set HTTP password"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Walk on names and valid with form.
        F = Storage_Form(data=opts)
        if F.is_valid():
            s = F.save()
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'name': 'Name', 'address': 'Address', 'port': 'Port', 'url_prefix': 'URL prefix', 'protocol': 'Protocol', 'login': 'Login'}))
            self.stdout.write(ROW_FORMAT.format(**s.__dict__))
        elif not opts['quiet']:
            self.stdout.write('* Error(s)')
            for f,errs in F.errors.items():
                self.stdout.write(f)
                for err in errs:
                    self.stdout.write('\t'+err)


class Modify_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', help="Select storages by IDs separated by comma"),
        make_option('-n', '--name', action='store', default=None, help="Set name"),
        make_option('-a', '--address', action='store', default=None, help="Set IP or FQDN"),
        make_option('-p', '--port', action='store', default=None, help="Set port"),
        make_option('-u', '--url_prefix', action='store', default=None, help="Set url prefix"),
        make_option('-P', '--protocol', action='store', default=None, help="Set HTTP or HTTPS"),
        make_option('-l', '--login', action='store', default=None, help="Set HTTP login"),
        make_option('-w', '--password', action='store', default=None, help="Set HTTP password"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select storage by id
        ids = [ i.strip() for i in opts['ids'].split(',') ]
        storages = Storage.objects.filter(id__in=ids)
        if not storages.exists():
            self.stdout.write("No storage with id '%s' exists." % opts['id'])
            sys.exit(1)
        existing_ids = [ s.id for s in storages ]
        non_existing_ids = [ id for id in ids if int(id) not in existing_ids ]
        modified_storages = []
        form_error = None
        # Format options to left 'None'
        opts = dict([ (k,v) for k,v in opts.items() if v is not None ])
        # Walk on host for valid or fail
        for s in storages:
            # Make validation
            # Create new data computing instance and options
            data = dict( [ (key.replace('_id', ''),val) for key,val in s.__dict__.items() ] )
            data.update(opts)
            # Use Form to valid
            F = Storage_Form(data=data, instance=s)
            if F.is_valid():
                h = F.save()
                modified_storages.append(s)
            else:
                form_error = F.errors

        # Walk on all list to print it
        if modified_storages:
            self.stdout.write('* Storage(s) updated:')
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'name': 'Name', 'address': 'Address', 'port': 'Port', 'url_prefix': 'URL prefix', 'protocol': 'Protocol', 'login': 'Login'}))
            for s in modified_storages:
                self.stdout.write(ROW_FORMAT.format(**s.__dict__))

        if non_existing_ids:
            self.stdout.write('* No storage with following IDs:') 
            for id in non_existing_ids:
                self.stdout.write(id)
        if form_error:
            self.stdout.write('* Error:')
            for field,errors in form_error.items():
                self.stdout.write(field)
                for err in errors:
                    self.stdout.write('\t'+err)
