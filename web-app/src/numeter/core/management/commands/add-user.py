from django.core.management.base import BaseCommand, CommandError

from core.models import User, GraphLib

from optparse import make_option
from getpass import getpass
import logging


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-u', '--username', action='store', default=False, help="Set username"),
        make_option('-e', '--email', action='store', default=False, help="Set email"),
        make_option('-S', '--superuser', action='store', default=False, help="Set as superuser"),
        make_option('-g', '--graphlib', action='store', default=False, help="Set graph library"),
        make_option('-p', '--password', action='store', default=False, help="Set password"),
    )

    def handle(self, *args, **options):
        # Set username
        if not options['username']:
            options['username'] = raw_input('Username > ')
        # Set email
        if not options['email']:
            options['email'] = raw_input('Email (optionnal) > ')
        # Set if is superuser
        if not options['superuser']:
            options['superuser'] = raw_input('Is superuser [Y/n] > ') or 'y'
        # Set graph lib
        if not options['graphlib']:
            Gs = GraphLib.objects.all()
            graphlib_list = [ G.name for G in Gs ]
            if Gs.count() > 1 :
                print '\n'.join([ ('%s: %s' % (i, n)) for i, n in enumerate(graphlib_list) ])
                num = int(raw_input('Which library do you choose ? : '))
                options['graphlib'] = graphlib_list[num]
            else:
                options['graphlib'] = graphlib_list[0]
                print 'Graph library: %s' % options['graphlib']

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
            is_active=True
        )
        U.set_password(options['password'])
        U.save()
        logging.info(u"Create user '%s' in Db" % U.username)
