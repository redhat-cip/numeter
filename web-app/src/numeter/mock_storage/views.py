from django.http import HttpResponse
from django.conf import settings
BASEDIR = settings.BASEDIR
#from mock_storage.models import Host


def hosts(request):
    with open(BASEDIR+'/../mock_storage/fixtures/hosts.json') as f:
        response = f.read()
    return HttpResponse(response)


def hinfo(request):
    #request.GET['host']
    with open(BASEDIR+'/../mock_storage/fixtures/hinfo.json') as f:
        response = f.read()
    return response


def list(request):
    #request.GET['host']
    with open(BASEDIR+'/../mock_storage/fixtures/host.json') as f:
        response = f.read()
    return response


def data(request):
    #request.GET['host']
    #request.GET['plugin']
    #request.GET['ds']
    #request.GET['res']
    with open(BASEDIR+'/../mock_storage/fixtures/data.json') as f:
        response = f.read()
    return response
