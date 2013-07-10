from django.http import HttpResponse
from django.conf import settings
BASEDIR = settings.BASEDIR

from mock_storage.models import Host
from mock_storage.utils import get_hosts_json, get_host_json, get_list_json

from json import load as jload, loads as jloads, dumps as jdumps
from random import random, randrange


def hosts(request):
    return HttpResponse(get_hosts_json())


def hinfo(request):
    host_json = get_host_json(reques.GET['host'])
    return HttpResponse(host_json)


def list(request):
    return HttpResponse(get_list_json())


def data(request):
    r = {
        "TS_start": 1372951380,
        "TS_step": 60,
        "DATAS": {"nice": [] }
    }
    val = random() * 100
    for i in range(100):
        r['DATAS']['nice'].append( val )
        val += randrange(-5,5,0.1,float)
    r = jdumps(r)
        
    return HttpResponse(r)
