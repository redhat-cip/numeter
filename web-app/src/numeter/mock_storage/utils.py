from json import load as jload, loads as jloads
from django.conf import settings
BASEDIR = settings.BASEDIR


def get_hosts_json():
    with open(BASEDIR+'/../mock_storage/fixtures/hosts.json') as f:
        return f.read()


def get_host_json(hostid):
    hosts_json = get_hosts_json()
    hosts = jloads(hosts_json)
    return hosts[hostid]


def get_list_json():
    with open(BASEDIR+'/../mock_storage/fixtures/list.json') as f:
        response = f.read()
    return response
