from django.http import HttpResponse
from django.conf import settings
BASEDIR = settings.BASEDIR

from mock_storage.models import Host
from mock_storage.utils import get_hosts_json, get_host_json, get_list_json

from json import load as jload, loads as jloads


def hosts(request):
    return HttpResponse(get_hosts_json())


def hinfo(request):
    host_json = get_host_json(reques.GET['host'])
    return HttpResponse(host_json)


def list(request):
    return HttpResponse(get_list_json())


def data(request):
    #request.GET['host']
    #request.GET['plugin']
    #request.GET['ds']
    #request.GET['res']
    with open(BASEDIR+'/../mock_storage/fixtures/data.json') as f:
        r = f.read()
    return HttpResponse(r)
