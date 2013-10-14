from django.core.management.base import BaseCommand, CommandError

from core.models import Storage, Host

from optparse import make_option
import logging


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
    )

    def handle(self, *args, **options):
        Storage.objects.create_hosts()
        for h in Host.objects.all():
            h.create_plugins()
        for p in Plugin.objects.all()
            p.create_data_sources()
