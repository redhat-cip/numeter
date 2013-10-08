from django.core.management.base import BaseCommand, CommandError

from core.models import Host
from core.models import Host

from optparse import make_option
import logging


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-n', '--name', action='store', default=None, help="Set name"),
        make_option('-a', '--address', action='store', default=False, help="Set IP or FQDN"),
        make_option('-p', '--port', action='store', default=8080, help="Set port"),
        make_option('-u', '--urlprefix', action='store', default='', help="Set url prefix"),
        make_option('-P', '--protocol', action='store', default='HTTP', help="Set HTTP or HTTPS"),
        make_option('-l', '--login', action='store', default='', help="Set HTTP login"),
        make_option('-w', '--password', action='store', default='', help="Set HTTP password"),
    )

    def handle(self, *args, **opts):
        if not args:
            pass
        elif args[0] == 'list':
            self._list(**opts)
        elif args[0] == 'add':
            self._add(*args, **opts)
        elif args[0] in ('delete','del'):
            pass
        elif args[0] in ('modify','mod'):
            pass

    def _list(self, **opts):
        hosts = Host.objects.values()
        row_format = '%(id)s | %(name)s | %(hostid)s | %(storage_id)s | %(group_id)s'
        self.stdout.write(row_format % {u'id': 'ID', 'group_id': 'Group ID', 'hostid': 'Host ID', 'name': u'Name', 'storage_id': 'Storage ID'})
        for h in hosts:
            self.stdout.write(row_format % h)

    def _add(self, **opts):
        if not 'hostid' in opts:
            pass
