from django.http import HttpResponse
from django.conf import settings
BASEDIR = settings.BASEDIR

from mock_storage.models import Host
from mock_storage.utils import get_hosts_json, get_host_json, get_list_json

from json import load as jload, loads as jloads, dumps as jdumps
from random import random, randrange


def index(request, id):
    text = """<h3>Available functions:</h3>
    <ul>
     <li>[12]/numeter-storage/hosts</li>
     <li>[12]/numeter-storage/hinfo</li>
     <li>[12]/numeter-storage/list</li>
     <li>[12]/numeter-storage/data</li>
    </ul>
    """
    return HttpResponse(text)

def hosts(request, id):
    return HttpResponse(get_hosts_json(id))


def hinfo(request, id):
    host_json = get_host_json(request.GET['host'], id)
    return HttpResponse(jdumps(host_json))


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
        val += randrange(-5,6,0.1,float)
    r = jdumps(r)
        
    return HttpResponse(r)
