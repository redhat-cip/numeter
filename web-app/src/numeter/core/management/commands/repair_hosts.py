from django.core.management.base import BaseCommand, CommandError

from core.models import Storage, Host

from optparse import make_option
import logging


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-f', '--force', action='store_true', default=False, help="Skip asking"),
    )

    def handle(self, *args, **options):
        hosts = Host.objects.filter(hostid__in=Storage.objects.get_bad_referenced_hostids())

        if not hosts.exists():
            print 'No broken host to repair.'
            return

        print 'Broken host(s):'
        print '\n'.join([ ('%s => %s' % (h,h.storage)) for h in hosts ] )

        if not options['force']:
            if raw_input('Do you really want to launch fixing ? (Y/n) : ') in 'nN':
                print 'Aborted!'
                return

        Storage.objects.repair_hosts()
        hosts = Host.objects.filter(pk__in= [ h.id for h in hosts ])
        
        print 'Result:'
        print '\n'.join([ ('%s => %s' % (h,h.storage)) for h in hosts ])
