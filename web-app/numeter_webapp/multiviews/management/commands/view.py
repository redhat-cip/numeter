from django.core.management.base import BaseCommand, CommandError

from core.models import Host, Plugin, Data_Source as Source
from multiviews.models import Skeleton, View
from configuration.forms.view import View_Form
from core.management.commands._utils import CommandDispatcher

from optparse import make_option
from os import devnull
import sys


class Command(CommandDispatcher):
    """View management base command."""
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


ROW_FORMAT = '{id:5} | {name:40} | {sources:30}'
class List_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
    )
    def handle(self, *args, **opts):
        self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'sources': 'Source IDs', 'name': u'Name'}))
        for v in View.objects.all():
            v_dict = v.__dict__
            v_dict['sources'] = ','.join([ str(s.id) for s in v.sources.all() ])
            self.stdout.write(ROW_FORMAT.format(**v_dict))
        # Print count
        self.stdout.write('Count: %i' % View.objects.count())


class Add_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-n', '--name', action='store', help="Set name."),
        make_option('-s', '--sources', action='store', help="Set sources."),
        make_option('-C', '--comment', action='store', default=None, help="Set comment."),
        make_option('-q', '--quiet', action='store_true', help="Don't print info."),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select source by id or ids
        opts['sources'] = [ i.strip() for i in opts['sources'].split(',') ]
        # Use Form to valid
        F = View_Form(data=opts)
        if F.is_valid():
            v = F.save()
            v_dict = v.__dict__
            v_dict['sources'] = ','.join([ str(s.id) for s in v.sources.all() ])
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'sources': 'Source IDs', 'name': u'Name'}))
            self.stdout.write(ROW_FORMAT.format(**v_dict))
        else:
            for field,errors in F.errors.items():
                self.stdout.write(field)
                for err in errors:
                    self.stdout.write('\t'+err)


class Delete_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default=None, help="Select views by ID separated by comma"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select view by ids
        if opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
            views = View.objects.filter(id__in=ids)
        else:
            self.stdout.write("You must give one or more ID.")
            self.print_help('view', 'help')
            sys.exit(1)
        # Stop if no given id
        if not views.exists():
            self.stdout.write("There's no view with given ID: '%s'" % (opts['ids'] or opts['id']) )
            sys.exit(1)
        for s in views:
            s.delete()
            self.stdout.write('Delete view: %s' % s)


class Modify_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', help="Select view by ID separated by comma"),
        make_option('-n', '--name', action='store', default=None, help="Set name."),
        make_option('-s', '--sources', action='store', default=None, help="Set sources, will remove existing."),
        make_option('--add-sources', action='store', default='', help="Add sources."),
        make_option('--rm-sources', action='store', default='', help="Remove sources."),
        make_option('-C', '--comment', action='store', default=None, help="Set comment."),
        make_option('-q', '--quiet', action='store_true', help="Don't print info."),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select view by id or ids
        ids = [ i.strip() for i in opts['ids'].split(',') ]
        views = View.objects.filter(id__in=ids)
        # Stop if no given id
        if not views.exists():
            self.stdout.write("There's no view with given ID: '%s'" % (opts['ids'] or opts['id']) )
            sys.exit(1)
        # Set source to add or del
        to_add = set([ i.strip() for i in opts['add_sources'].split(',') ])
        to_del = set([ i.strip() for i in opts['rm_sources'].split(',') ])
        # Walk on view for valid or fail
        modified_views = []
        form_error = None
        for v in views:
            # Use Form to valid
            data = v.__dict__
            data.update(dict([ (k,V) for k,V in opts.items() if V ]))
            data['sources'] = [ str(V.id) for V in v.sources.all() ]
            data['sources'] = set(data['sources']) - to_del
            data['sources'] = list(data['sources'] | to_add)
            data['sources'] = [ i for i in data['sources'] if i ]
            F = View_Form(data=data, instance=v)
            if F.is_valid():
                v = F.save()
                modified_views.append(v)
            else:
                form_error = F.errors
        # Walk on all list to print it
        if modified_views:
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'sources': 'Source IDs', 'name': u'Name'}))
            for v in modified_views:
                v_dict = v.__dict__
                v_dict['sources'] = ','.join([ str(s.id) for s in v.sources.all() ])
                self.stdout.write(ROW_FORMAT.format(**v_dict))

        if form_error:
            self.stdout.write('* Error:')
            for field,errors in form_error.items():
                self.stdout.write(field)
                for err in errors:
                    self.stdout.write('\t'+err)
