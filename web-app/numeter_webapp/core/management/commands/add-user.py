from django.core.management.base import BaseCommand, CommandError

from core.models import User
from core.models.utils import MediaList

from optparse import make_option
from getpass import getpass
from logging import getLogger
logger = getLogger('main')


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-u', '--username', action='store', default=False, help="Set username"),
        make_option('-e', '--email', action='store', default='', help="Set email"),
        make_option('-S', '--superuser', action='store_true', default=False, help="Set as superuser"),
        make_option('-g', '--graphlib', action='store', default=False, help="Set graph library as filename separated by ','"),
        make_option('-p', '--password', action='store', default=False, help="Set password"),
    )

    def handle(self, *args, **options):
        # Set username
        if not options['username']:
            options['username'] = raw_input('Username > ')
        # Set graph lib
        if not options['graphlib']:
            graphlib_list = MediaList()._list_available()
            if len(graphlib_list) > 1 :
                print '\n'.join([ ('%s: %s' % (i, n)) for i, n in enumerate(graphlib_list) ])
                nums = raw_input("Which file do you choose ? (separated by ',') : ")
                options['graphlib'] = [ graphlib_list[int(i)] for i in nums.split(',') ]
                print options['graphlib']
            else:
                options['graphlib'] = graphlib_list[0]
        else:
            # Convert string with ',' to list
            options['graphlib'] = [ s for s in options['graphlib'].split(',') ]

        # Set password
        if not options['password']:
            pass1, pass2 = str(''), str(' ')
            while pass1 != pass2:
                pass1 = getpass('Password >')
                pass2 = getpass('Confirmation >')
                if pass1 != pass2:
                    print 'Wrong password confirmation !'
            options['password'] = pass1


        # Create user
        U = User(
            username=options['username'],
            email=options['email'],
            is_staff=options['superuser'],
            is_superuser=options['superuser'],
            is_active=True,
            graph_lib=options['graphlib']
        )
        U.set_password(options['password'])
        U.save()
        
        logger.debug(u"Create user '%s' in Db" % U.username)
