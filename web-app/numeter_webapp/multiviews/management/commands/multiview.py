from django.core.management.base import BaseCommand, CommandError

from multiviews.models import View, Multiview
from configuration.forms.multiview import Multiview_Form
from core.management.commands._utils import CommandDispatcher

from optparse import make_option
from os import devnull
import sys


class Command(CommandDispatcher):
    """Multiview management base command."""
    actions = ('list','add','delete','del','modify','mod')
    def _subcommand_names(self):
        return ('list','add','delete','del','modify','mod')

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
        elif args[0] in ('modify','mod'):
            return Modify_Command()


ROW_FORMAT = '{id:5} | {name:30} | {views:40}'
class List_Command(BaseCommand):
    def handle(self, *args, **opts):
        multiviews = Multiview.objects.all()
        self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'views': 'Views ID', 'name': u'Name'}))
        for m in multiviews:
            m_data = m.__dict__
            m_data['views'] = ','.join([ str(_m.id) for _m in m.views.all() ])
            self.stdout.write(ROW_FORMAT.format(**m_data))
        self.stdout.write('Count: %i' % len(multiviews))


class Delete_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default=None, help="Select multiviews by ID separated by comma"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select view by ids
        ids = [ i.strip() for i in opts['ids'].split(',') if i ]
        multiviews = Multiview.objects.filter(id__in=ids)
        multiviews = multiviews if opts['ids'] else []
        for m in multiviews:
            m.delete()
            self.stdout.write('Delete multiview: %s' % m)


class Add_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-n', '--name', action='store', default='', help="Set name"),
        make_option('-V', '--views', action='store', default='', help="Set views, will remove existing."),
        make_option('-c', '--comment', action='store', default='', help="Set commment"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Format field
        view_ids = [ i.strip() for i in opts['views'].split(',') ]
        opts['views'] = view_ids
        F = Multiview_Form(data=opts)
        if F.is_valid():
            m = F.save()
            m_data = m.__dict__
            m_data['views'] = ','.join([ str(_v.id) for _v in m.views.all() ])
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'views': 'Views ID', 'name': u'Name'}))
            self.stdout.write(ROW_FORMAT.format(**m_data))
        elif not opts['quiet']:
            self.stdout.write('* Error(s)')
            for f,errs in F.errors.items():
                self.stdout.write(f)
                for err in errs:
                    self.stdout.write('\t'+err)


class Modify_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--id', action='store', type='int', help="Select a multiview by ID"),
        make_option('-n', '--name', action='store', default='', help="Set name"),
        make_option('-V', '--views', action='store', default='', help="Set views, will remove existing."),
        make_option('-c', '--comment', action='store', default='', help="Set commment"),
        make_option('-q', '--quiet', action='store_true', default=False, help="Don't print info"),
        make_option('-G', '--groups', action='store', default='', help="Set groups, will remove existing."),
        make_option('--add-views', action='store', default='', help="Add views."),
        make_option('--rm-views', action='store', default='', help="Remove views."),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Set view to add or del
        to_set = set([ i.strip() for i in opts.pop('views', '').split(',') if i ])
        to_add = set([ i.strip() for i in opts.pop('add_views', '').split(',') ])
        to_del = set([ i.strip() for i in opts.pop('rm_views', '').split(',') ])
        opts = dict([ (k,v) for k,v in opts.items() if v is not None ])
        # Valid and save
        m = Multiview.objects.get(id=opts['id'])
        data = m.__dict__
        data.update(dict([ (k,v) for k,v in opts.items() if v ]))
        data['views'] = to_set or [ str(v.id) for v in m.views.all() ]
        data['views'] = set(data['views']) - to_del
        data['views'] = list(data['views'] | to_add)
        data['views'] = [ i for i in data['views'] if i ]
        F = Multiview_Form(data=data, instance=m)
        if F.is_valid():
            m = F.save()
            m_data = m.__dict__
            m_data['views'] = ','.join([ str(_v.id) for _v in m.views.all() ])
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'views': 'Views ID', 'name': u'Name'}))
            self.stdout.write(ROW_FORMAT.format(**m_data))
        elif not opts['quiet']:
            self.stdout.write('* Error(s)')
            for field,errors in F.errors.items():
                self.stdout.write(field)
                for err in errors:
                    self.stdout.write('\t'+err)
