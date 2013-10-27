from django.core.management.base import BaseCommand, CommandError

from core.models import Host, Plugin, Data_Source as Source
from multiviews.models import Skeleton, View
from configuration.forms.skeleton import Skeleton_Form
from core.management.commands._utils import CommandDispatcher

from optparse import make_option
from os import devnull
import sys


class Command(CommandDispatcher):
    """Host management base command."""
    actions = ('list','add','delete','del','modify','mod','create_view')

    def _subcommand_names(self):
        return ('list','add','delete','del','modify','mod','create_view')

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
        elif args[0] == 'create_view':
            return Create_View_Command()


ROW_FORMAT = '{id:5} | {name:40} | {plugin_pattern:20} | {source_pattern:20}'
class List_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
    )
    def handle(self, *args, **opts):
        self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'plugin_pattern': 'Plugin pattern', 'source_pattern': 'Source Pattern', 'name': u'Name'}))
        for s in Skeleton.objects.all():
            self.stdout.write(ROW_FORMAT.format(**s.__dict__))
        # Print count
        self.stdout.write('Count: %i' % Skeleton.objects.count())


class Add_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-n', '--name', action='store', default=None, help="Set name."),
        make_option('-p', '--plugin_pattern', action='store', default=None, help="Set plugin pattern."),
        make_option('-s', '--source_pattern', action='store', default=None, help="Set source pattern."),
        make_option('-C', '--comment', action='store', default=None, help="Set comment."),
        make_option('-q', '--quiet', action='store_true', help="Don't print info."),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Use Form to valid
        F = Skeleton_Form(data=opts)
        if F.is_valid():
            s = F.save()
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'plugin_pattern': 'Plugin pattern', 'source_pattern': 'Source Pattern', 'name': u'Name'}))
            self.stdout.write(ROW_FORMAT.format(**s.__dict__))
        else:
            for field,errors in F.errors.items():
                self.stdout.write(field)
                for err in errors:
                    self.stdout.write('\t'+err)


class Delete_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default=None, help="Select skeletons by ID separated by comma"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select host by id or ids
        if opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
            skeletons = Skeleton.objects.filter(id__in=ids)
        else:
            self.stdout.write("You must give one or more ID.")
            self.print_help('skeleton', 'help')
            sys.exit(1)
        # Stop if no given id
        if not skeletons.exists():
            self.stdout.write("There's no skeleton with given ID: '%s'" % (opts['ids'] or opts['id']) )
            sys.exit(1)
        for s in skeletons:
            s.delete()
            self.stdout.write('Delete skeleton: %s' % s)


class Modify_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', help="Select skeletons by ID separated by comma"),
        make_option('-n', '--name', action='store', default=None, help="Set name."),
        make_option('-p', '--plugin_pattern', action='store', default=None, help="Set plugin pattern."),
        make_option('-s', '--source_pattern', action='store', default=None, help="Set source pattern."),
        make_option('-C', '--comment', action='store', default=None, help="Set comment."),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select host by id or ids
        ids = [ i.strip() for i in opts['ids'].split(',') ]
        skeletons = Skeleton.objects.filter(id__in=ids)
        # Stop if no given id
        if not skeletons.exists():
            self.stdout.write("There's no skeleton with given ID: '%s'" % (opts['ids'] or opts['id']) )
            sys.exit(1)
        # Walk on skeleton for valid or fail
        modified_skeletons = []
        form_error = None
        for s in skeletons:
            # Use Form to valid
            data = s.__dict__
            data.update(dict([ (k,v) for k,v in opts.items() if v ]))
            F = Skeleton_Form(data=data, instance=s)
            if F.is_valid():
                s = F.save()
                modified_skeletons.append(s)
            else:
                form_error = F.errors
        # Walk on all list to print it
        if modified_skeletons:
            self.stdout.write('* Skeleton updated:')
            for s in modified_skeletons:
                self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'plugin_pattern': 'Plugin pattern', 'source_pattern': 'Source Pattern', 'name': u'Name'}))
                self.stdout.write(ROW_FORMAT.format(**s.__dict__))

        if form_error:
            self.stdout.write('* Error:')
            for field,errors in form_error.items():
                self.stdout.write(field)
                for err in errors:
                    self.stdout.write('\t'+err)


VIEW_ROW_FORMAT = '{id:5} | {name:30} | {sources:50}'
class Create_View_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--id', action='store', help="Select skeleton by ID separated by comma"),
        make_option('-I', '--hostids', action='store', help="Select hosts by ID separated by comma"),
        make_option('-n', '--name', action='store', default=None, help="Set view name."),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select skeleton by id or ids
        if Skeleton.objects.filter(id=opts['id']).exists():
            skeleton = Skeleton.objects.get(id=opts['id'])
        else:
            self.stdout.write("There's no skeleton with given ID: '%s'" % opts['id'])
            sys.exit(1)
        # Select host by id or ids
        hostids = [ i.strip() for i in opts['hostids'].split(',') ]
        hosts = Host.objects.filter(hostid__in=hostids)
        # Stop if no given id
        if not hosts.exists():
            self.stdout.write("There's no skeleton with given ID: '%s'" % (opts['ids'] or opts['id']) )
            sys.exit(1)
        v = skeleton.create_view(opts['name'], hosts)
        v_data = v.__dict__
        v_data['sources'] = ', '.join([ str(s.id) for s in v.sources.all() ])
        self.stdout.write(VIEW_ROW_FORMAT.format(**{u'id': 'ID', 'name': 'Name', 'sources': 'Source'}))
        self.stdout.write(VIEW_ROW_FORMAT.format(**v_data))

