"""
Group management commands module.
"""

from django.core.management.base import BaseCommand, CommandError

from core.models import Group, Host, User
from configuration.forms.group import Group_Form
from core.management.commands._utils import CommandDispatcher

from optparse import make_option
from os import devnull
import sys


class Command(CommandDispatcher):
    """Group management base command."""
    actions = ('list','add','delete','del','modify','mod','hosts','users')
    def _subcommand_names(self):
        return ('list','add','delete','del','modify','mod','hosts','users')

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
        elif args[0] == 'hosts':
            return Hosts_Command()
        elif args[0] == 'users':
            return Users_Command()


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
        make_option('-i', '--ids', action='store', default=None, help="Select groups by ID separated by comma"),
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
            self.stdout.write("There's no group with given ID: '%s'" % opts['ids'] )
            sys.exit(1)
        for g in groups:
            g.delete()
            self.stdout.write('Delete group: %s' % g)


class Add_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-n', '--names', action='store', default='', help="Set multiple group name by ID separated by comma"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Format names
        if opts['names']:
            names = [ n.strip() for n in opts['names'].split(',') ]
        else:
            self.stdout.write("You must give one or more name.")
            self.print_help('group', 'help')
            sys.exit(1)

        self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'name': 'Name'}))
        # Walk on names and valid with form.
        form_errors = []
        for n in names:
            F = Group_Form(data={'name':n})
            if F.is_valid():
                g = F.save()
                self.stdout.write(ROW_FORMAT.format(**g.__dict__))
            else:
                form_errors.append((n,F.errors))
        self.stdout.write('Created count: %i' % (len(names) - len(form_errors)))
        # Print errors
        if form_errors and not opts['quiet']:
            self.stdout.write('* Error(s)')
            for n, errs in form_errors:
                self.stdout.write('* %s:' % n)
                for field,errors in errs.items():
                    self.stdout.write(field)
                    for err in errors:
                        self.stdout.write('\t'+err)


class Modify_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--id', action='store', type='int', help="Select a group by ID"),
        make_option('-n', '--name', action='store', help="Set name"),
        make_option('-q', '--quiet', action='store_true', help="Don't print info"),
    )

    def handle(self, *args, **opts):
        if opts['quiet']: self.stdout = open(devnull, 'w')
        # Select group by id
        if not Group.objects.filter(id=opts['id']).exists():
            self.stdout.write("No group with id '%s' exists." % opts['id'])
            sys.exit(1)
        # Valid and save
        g = Group.objects.get(id=opts['id'])
        F = Group_Form(data=opts, instance=g)
        if F.is_valid():
            g = F.save()
            self.stdout.write(ROW_FORMAT.format(**{u'id': 'ID', 'name': 'Name'}))
            self.stdout.write(ROW_FORMAT.format(**g.__dict__))

        elif not opts['quiet']:
            self.stdout.write('* Error(s)')
            for field,errors in F.errors.items():
                self.stdout.write(field)
                for err in errors:
                    self.stdout.write('\t'+err)


HOST_ROW_FORMAT = '{id:5} | {name:40} | {hostid:50} | {storage_id:10} | {group_id:9}'
class Hosts_Command(BaseCommand):
    """
    Custom host listing by group.
    Dealing only with hosts saved in database.
    """
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default='', help="Select groups by ID separated by comma"),
    )

    def handle(self, *args, **opts):
        # Select group by id or ids
        ids = [ i.strip() for i in opts['ids'].split(',') if i ]
        groups = Group.objects.filter(id__in=ids) or Group.objects.all()
        # Walk on groups and list hosts
        self.stdout.write(HOST_ROW_FORMAT.format(**{u'id': 'ID', 'group_id': 'Group ID', 'hostid': 'Host ID', 'name': u'Name', 'storage_id': 'Storage ID'}))
        for g in groups:
            for h in Host.objects.filter(group=g):
                self.stdout.write(HOST_ROW_FORMAT.format(**h.__dict__))
        for h in Host.objects.filter(group=None):
            self.stdout.write(HOST_ROW_FORMAT.format(**h.__dict__))


USER_ROW_FORMAT = '{id:5} | {username:30} | {is_superuser:10} | {graph_lib:15} | {groups:20}'
class Users_Command(BaseCommand):
    """Custom user listing by group."""
    option_list = BaseCommand.option_list + (
        make_option('-i', '--ids', action='store', default=None, help="Select hosts by ID separated by comma"),
    )

    def handle(self, *args, **opts):
        # Select group by id or ids
        if opts['ids']:
            ids = [ i.strip() for i in opts['ids'].split(',') ]
            groups = Group.objects.filter(id__in=ids)
        else:
            groups = Group.objects.all()
        # Stop if no given id
        if not groups.exists():
            self.stdout.write("There's no group with given ID: '%s'" % opts['ids'] )
            sys.exit(1)
        # Walk on groups and list hosts
        self.stdout.write(USER_ROW_FORMAT.format(**{u'id': 'ID', 'groups': 'Groups ID', 'is_superuser': 'Superuser', 'username': u'Userame', 'graph_lib': 'Graph lib'}))
        for g in groups:
            for u in User.objects.filter(groups=g):
                u_data = u.__dict__
                u_data['groups'] = ','.join([ str(_g.id) for _g in u.groups.all() ])
                u_data['graph_lib'] = ','.join(u_data['graph_lib'])
                self.stdout.write(USER_ROW_FORMAT.format(**u_data))
