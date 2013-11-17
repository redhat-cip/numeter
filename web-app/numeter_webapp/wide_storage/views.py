"""
wide_storage view module.
"""

from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from core.models import Storage, Host


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hosts(request):
    user_hostids = [ h.hostid for h in Host.objects.user_filter(request.user) ]
    data = {}
    [ data.update(s.get_hosts()) for s in Storage.objects.all() ]
    [ data.pop(k) for k,v in data.items() if not k in user_hostids ]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hinfo(request):
    get_object_or_404(Host.objects.user_filter(request.user).filter(hostid=request.GET['host']))
    storage = Storage.objects.which_storage(request.GET['host'])
    return Response(storage.get_info(request.GET['host']))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list(request):
    get_object_or_404(Host.objects.user_filter(request.user).filter(hostid=request.GET['host']))
    storage = Storage.objects.which_storage(request.GET['host'])
    return Response(storage._connect('plugins', {'hostid':request.GET['host']}))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def info(request):
    get_object_or_404(Host.objects.user_filter(request.user).filter(hostid=request.GET['host']))
    storage = Storage.objects.which_storage(request.GET['host'])
    return Response(storage.get_plugin_data_sources(request.GET['host'], request.GET['plugin']))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def data(request):
    get_object_or_404(Host.objects.user_filter(request.user).filter(hostid=request.GET['host']))
    storage = Storage.objects.which_storage(request.GET['host'])
    req = {
        'hostid':request.GET['host'],
        'plugin':request.GET['plugin'],
        'ds':request.GET['ds'],
        'res':request.GET['res'],
    }
    return Response(storage.get_data(**req))
