from django.core.management.base import BaseCommand, CommandError

from core.models import User

from optparse import make_option
from logging import getLogger
logger = getLogger('main')


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-u', '--username', action='store', default=False, help="Find by username"),
        make_option('-f', '--force', action='store', default=False, help="Skip asking"),
    )

    def handle(self, *args, **options):
        Us = User.objects.all()
        # Stop if there's no user in Db
        if Us.count() == 0:
            print "There's no user in database."
            return

        # If there's only 1 storage, choose it
        if Us.count() == 1:
            pass

        # Search user by args or asking
        else:
            if not options['username']:
                name_list = [ U.username for U in Us ]
                print '\n'.join([ ('%s: %s' % (i, n)) for i, n in enumerate(name_list) ])
                num = int(raw_input('Which user do you choose ? : '))
                options['username'] = name_list[num]
            Us = Us.filter(username=options['username'])

        U = Us.get()

        if not options['force']:
            if raw_input("Do you really want to delete '%s' ? [N/y] " % U) != 'y':
                print 'Aborted !'
                return

        U.delete()
        logger.debug(u"Delete delete '%s' in Db" % U.__unicode__())
