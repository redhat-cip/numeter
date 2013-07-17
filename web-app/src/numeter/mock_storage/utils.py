from json import load as jload, loads as jloads
from django.conf import settings
BASEDIR = settings.BASEDIR


def get_hosts_json(mock_id):
    with open(BASEDIR+'/../mock_storage/fixtures/hosts%s.json' % mock_id) as f:
        return f.read()


def get_host_json(hostid, mock_id):
    hosts_json = get_hosts_json(mock_id)
    hosts = jloads(hosts_json)
    return hosts.get(hostid, {})


def get_list_json():
    with open(BASEDIR+'/../mock_storage/fixtures/list.json') as f:
        response = f.read()
    return response
