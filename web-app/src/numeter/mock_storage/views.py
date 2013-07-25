from django.http import HttpResponse
from django.conf import settings
BASEDIR = settings.BASEDIR

from mock_storage.models import Host
from mock_storage.utils import get_hosts_json, get_host_json, get_list_json

from json import load as jload, loads as jloads, dumps as jdumps
from random import random, randrange


res = {
  'Daily': 60, # Hour
  'Weekly': 720, # Half-day
  'Monthly': 1140, # Day
  'Yearly': 17100 # Half-month
}


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
    sources = request.GET['ds'].split(',')
    r = {
        "TS_start": 1372951380,
        "TS_step": res[request.GET['res']],
        "DATAS": dict([ (k,[]) for k in sources ])
    }
    val = random() * 100
    for s in r["DATAS"]:
        for i in range(100):
            r['DATAS'][s].append( val )
            val += randrange(-5,6,0.1,float)
    r = jdumps(r)
        
    return HttpResponse(r)
