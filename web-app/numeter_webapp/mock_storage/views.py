from django.http import HttpResponse
from django.utils.timezone import now
from django.conf import settings
BASEDIR = settings.BASEDIR

from mock_storage.models import Host
from mock_storage.sources import full_random, sinus, linear, random_func, delta_of
from mock_storage.utils import get_hosts_json, get_host_json, get_list_json
from mock_storage.utils import get_start_date

from json import load as jload, loads as jloads, dumps as jdumps
from random import random, randrange, randint


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


def list(request, id):
    return HttpResponse(get_list_json(id))


def data(request, id):
    sources = request.GET['ds'].split(',')
    start_date = get_start_date(request.GET['res'])
    step = res[request.GET['res']]
    step_num = int((now() - start_date).total_seconds() / 60) / step
    r = {
      "TS_start": int(start_date.strftime('%s')),
      "TS_step": step*60,
      "DATAS": dict([ (k,[]) for k in sources ])
    }
    if len(sources) == 2:
        for val in random_func(step_num, offset_y=randint(0, 100), min_y=0):
            r['DATAS'][sources[0]].append(val)
        for val in delta_of(r['DATAS'][sources[0]]):
            r['DATAS'][sources[1]].append(val)
    else:        
        for s in sources:
            for val in random_func(step_num):
                r['DATAS'][s].append( val )
    r = jdumps(r)
    return HttpResponse(r)
