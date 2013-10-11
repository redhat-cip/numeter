from django.core.management.base import BaseCommand, CommandError

from core.models import Group
from configuration.forms.group import Group_Form
from core.management.commands._utils import CommandDispatcher

from optparse import make_option
import sys


class Command(CommandDispatcher):
    """Group management base command."""
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


ROW_FORMAT = '{id:5} | {name:40}'
class List_Command(BaseCommand):
    def handle(self, *args, **opts):
        groups = Group.objects.values()
        self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'name': 'Name'}))
        for g in groups:
            self.stdout.write(ROW_FORMAT.format(**g))
        self.stdout.write('Count: %i' % len(groups))


class Delete_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default=None, help="Select group by ID separated by comma"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select group by ids
        if opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
            groups = Group.objects.filter(id__in=ids)
        else:
            self.stdout.write("You must give one or more ID.")
            self.print_help('group', 'help')
            sys.exit(1)
        # Stop if no given id
        if not groups.exists():
            self.stdout.write("There's no group with given ID: '%s'" % (opts['ids'] or opts['id']) )
            sys.exit(1)
        for g in groups:
            g.delete()
            self.stdout.write('Delete group: %s' % g)
