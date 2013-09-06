from django.core.management.base import BaseCommand, CommandError

from core.models import Storage

from optparse import make_option
import logging


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-A', '--alias', action='store', default=None, help="Set name"),
        make_option('-a', '--address', action='store', default=False, help="Set IP or FQDN"),
        make_option('-p', '--port', action='store', default=8080, help="Set port"),
        make_option('-u', '--urlprefix', action='store', default='', help="Set url prefix"),
        make_option('-P', '--protocol', action='store', default='HTTP', help="Set HTTP or HTTPS"),
        make_option('-l', '--login', action='store', default='', help="Set HTTP login"),
        make_option('-w', '--password', action='store', default='', help="Set HTTP password"),
    )

    def handle(self, *args, **options):
        # Set name
        if not options['alias']:
            options['alias'] = raw_input('Name (optionnal) > ')
        # Set addr
        if not options['address']:
            options['address'] = raw_input('Address or IP > ')

        if options['password']:
            logger.warning('Password is saved as raw in database. Be sure it has restricted access.')

        # Create user
        S = Storage(
            name=options['alias'],
            address=options['address'],
            port=options['port'],
            url_prefix=options['urlprefix'],
            protocol=options['protocol'],
            login=options['login'],
            password=options['password']
        )
        S.save()
        logging.info(u"Create storage '%s' in Db" % S.address)
