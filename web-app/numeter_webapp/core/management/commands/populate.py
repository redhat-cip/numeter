from django.core.management.base import BaseCommand, CommandError

from core.models import Storage, Host, Plugin, Data_Source as Source

from optparse import make_option
import logging


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
    )

    def handle(self, *args, **options):
        for s in Storage.objects.all():
            s.create_hosts()
        for h in Host.objects.all():
            h.create_plugins()
        for p in Plugin.objects.all():
            p.create_data_sources()
