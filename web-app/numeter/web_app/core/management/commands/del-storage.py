from django.core.management.base import BaseCommand, CommandError

from core.models import Storage

from optparse import make_option
import logging


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-A', '--alias', action='store', default=False, help="Find by name"),
        make_option('-a', '--address', action='store', default=False, help="Find by address"),
        make_option('-f', '--force', action='store_true', default=False, help="Skip asking"),
    )

    def handle(self, *args, **options):
        Ss = Storage.objects.all()
        # Stop if there's no user in Db
        if Ss.count() == 0:
            print "There's no storage in database."
            return

        # If there's only 1 storage, choose it
        if Ss.count() == 1:
            pass

        # Search storage by args or asking
        else:
            if not options['name']:
                name_list = [ S.name for S in Ss ]
                if len(name_list) > 1:
                    print '\n'.join([ ('%s: %s' % (i, n)) for i, n in enumerate(name_list) ])
                    num = int(raw_input('Which name do you choose ? : '))
                    options['name'] = name_list[num]
                else:
                    options['name'] = name_list[0]
            Ss = Ss.filter(name=options['name'])
            print(u"Name : %s" % options['name'])

            if not options['address']:
                address_list = [ S.address for S in Ss ]
                if len(address_list) > 1:
                    print '\n'.join([ ('%s: %s' % (i, s)) for i, s in enumerate(address_list) ])
                    num = int(raw_input('Which address do you choose ? : '))
                    options['address'] = address_list[num]
                else:
                    options['address'] = address_list[0]
            Ss = Ss.filter(address=options['address'])
            print(u"Address : %s" % options['address'])

        S = Ss.get()

        if not options['force']:
            if raw_input("Do you really want to delete '%s' ? [N/y] " % S) != 'y':
                logging.info('Aborted !')
                return

        S.delete()
        logging.info(u"Delete storage '%s' in Db" % S.__unicode__())
