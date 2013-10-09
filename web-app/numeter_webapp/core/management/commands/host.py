from django.core.management.base import BaseCommand, CommandError

from core.models import Storage, Host
from core.management.commands._utils import CommandDispatcher

from optparse import make_option
from argparse import ArgumentParser
import sys


class Command(CommandDispatcher):
    actions = ('list','add','delete','del','modify','mod')

    def usage(self, subcommand):
        """
        Return a brief description of how to use this command, by
        default from the attribute ``self.help``.
        """
        usage = '%%prog %s [action] [options] %s' % (subcommand, self.args)
        if self.help:
            return '%s\n\n%s' % (usage, self.help)
        else:
            return usage


    def _subcommand_names(self, name):
        return ('list','add','delete','del','modify','mod')

    def _subcommand(self, *args, **opts):
        if not args or args[0] not in self.actions:
            self.stdout.write(self.usage('host'))
            sys.exit(0)
        elif args[0] == 'list':
            return List_Command()
        elif args[0] == 'add':
            return Add_Command()
        elif args[0] in ('delete','del'):
            return Delete_Command()
        elif args[0] in ('modify','mod'):
            pass


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
        make_option('-i', '--id', action='store', default=None, help="Search host by ID"),
    )

    def handle(self, *args, **opts):
        storage = Storage.objects.which_storage(opts['id'])
        # Stop if not found
        if not storage:
            self.stdout.write('No host found with ID: %s' % opts['id'])
            sys.exit(1)
        # Repair and stop if already exists
        if Host.objects.filter(hostid=opts['id']).exists():
            self.stdout.write('Host with ID %s, already exists in db.' % opts['id'])
            host = Host.objects.get(hostid=opts['id'])
            if host.storage != storage:
                self.stdout.write("Host wasn't linked to good storage, now linked to %s" % storage)
                host.storage = storage
                host.save()
            sys.exit(1)
        # Create host
        host_info = storage.get_info(opts['id'])
        h = Host.objects.create(
            name=host_info['Name'],
            hostid=opts['id'],
            storage=storage,
            group=None
        )
        self.stdout.write('Host create: %s' % h)

class Delete_Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-i', '--id', action='store', default=None, help="Search host by ID"),
    )

    def handle(self, *args, **opts):
        # Stop if doesn't exist
        if not Host.objects.filter(hostid=opts['id']):
             self.stdout.write("Host doesn't exist")
        host = Host.objects.get(hostid=opts['id'])
        host.delete()
        self.stdout.write('Host delete.')
