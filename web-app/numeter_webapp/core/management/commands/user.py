"""
User management commands module.
"""

from django.core.management.base import BaseCommand, CommandError

from core.models import Group, User
from configuration.forms.user import User_CreationForm, User_Admin_EditForm
from core.management.commands._utils import CommandDispatcher

from optparse import make_option
from getpass import getpass
from os import devnull
import sys


class Command(CommandDispatcher):
    """User management base command."""
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


ROW_FORMAT = '{id:5} | {username:30} | {is_superuser:10} | {graph_lib:15} | {groups:20}'
class List_Command(BaseCommand):
    def handle(self, *args, **opts):
        users = User.objects.all()
        self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'groups': 'Groups ID', 'is_superuser': 'Superuser', 'username': u'Userame', 'graph_lib': 'Graph lib'}))
        for u in users:
            u_data = u.__dict__
            u_data['groups'] = ','.join([ str(_g.id) for _g in u.groups.all() ])
            self.stdout.write(ROW_FORMAT.format(**u_data))
        self.stdout.write('Count: %i' % len(users))


class Delete_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default=None, help="Select users by ID separated by comma"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select group by ids
        ids = [ i.strip() for i in opts['ids'].split(',') if i ]
        users = User.objects.filter(id__in=ids)
        users = users if opts['ids'] else []
        for u in users:
            u.delete()
            self.stdout.write('Delete user: %s' % u)


class Add_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-u', '--username', action='store', default='', help="Set username"),
        make_option('-e', '--email', action='store', default='', help="Set email"),
        make_option('-S', '--is_superuser', action='store_true', default=False, help="Set as superuser"),
        make_option('-g', '--graph_lib', action='store', default='dygraph', help="Set graph library"),
        make_option('-p', '--password', action='store', default=False, help="Set password"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Format field
        opts['username'] = opts['username'] or raw_input('Username > ')
        opts['password1'] = opts['password'] or getpass('Password >')
        opts['password2'] = opts['password'] or getpass('Confirmation >')
        F = User_CreationForm(data=opts)
        if F.is_valid():
            u = F.save()
            u_data = u.__dict__
            u_data['groups'] = ','.join([ str(_g.id) for _g in u.groups.all() ])
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'groups': 'Groups ID', 'is_superuser': 'Superuser', 'username': u'Userame', 'graph_lib': 'Graph lib'}))
            self.stdout.write(ROW_FORMAT.format(**u_data))
        elif not opts['quiet']:
            self.stdout.write('* Error(s)')
            for f,errs in F.errors.items():
                self.stdout.write(f)
                for err in errs:
                    self.stdout.write('\t'+err)


class Modify_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--id', action='store', type='int', help="Select a user by ID"),
        make_option('-u', '--username', action='store', default='', help="Set username"),
        make_option('-e', '--email', action='store', default='', help="Set email"),
        make_option('-g', '--graph_lib', action='store', default=None, help="Set graph library"),
        make_option('-q', '--quiet', action='store_true', default=False, help="Don't print info"),
        make_option('-G', '--groups', action='store', default='', help="Set groups, will remove existing."),
        make_option('--add-groups', action='store', default='', help="Add groups."),
        make_option('--rm-groups', action='store', default='', help="Remove groups."),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select group by id
        if not User.objects.filter(id=opts['id']).exists():
            self.stdout.write("No user with id '%s' exists." % opts['id'])
            sys.exit(1)
        # Set group to add or del
        to_set = set([ i.strip() for i in opts.pop('groups', '').split(',') if i ])
        to_add = set([ i.strip() for i in opts.pop('add_groups', '').split(',') ])
        to_del = set([ i.strip() for i in opts.pop('rm_groups', '').split(',') ])
        opts = dict([ (k,v) for k,v in opts.items() if v is not None ])
        # Valid and save
        u = User.objects.get(id=opts['id'])
        data = u.__dict__
        data.update(dict([ (k,v) for k,v in opts.items() if v ]))
        data['groups'] = to_set or [ str(U.id) for U in u.groups.all() ]
        data['groups'] = set(data['groups']) - to_del
        data['groups'] = list(data['groups'] | to_add)
        data['groups'] = [ i for i in data['groups'] if i ]
        F = User_Admin_EditForm(data=data, instance=u)
        if F.is_valid():
            u = F.save()
            u_data = u.__dict__
            u_data['groups'] = ','.join([ str(_g.id) for _g in u.groups.all() ])
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'groups': 'Groups ID', 'is_superuser': 'Superuser', 'username': u'Userame', 'graph_lib': 'Graph lib'}))
            self.stdout.write(ROW_FORMAT.format(**u_data))
        elif not opts['quiet']:
            self.stdout.write('* Error(s)')
            for field,errors in F.errors.items():
                self.stdout.write(field)
                for err in errors:
                    self.stdout.write('\t'+err)
