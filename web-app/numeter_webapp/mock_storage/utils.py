from django.utils.timezone import now
from django.conf import settings
BASEDIR = settings.BASEDIR
from json import load as jload, loads as jloads
from datetime import timedelta


def get_hosts_json(mock_id):
    with open(BASEDIR+'/../mock_storage/fixtures/hosts%s.json' % mock_id) as f:
        return f.read()


def get_host_json(hostid, mock_id):
    hosts_json = get_hosts_json(mock_id)
    hosts = jloads(hosts_json)
    return hosts.get(hostid, {})


def get_list_json(id):
    with open(BASEDIR+'/../mock_storage/fixtures/list%s.json' % id) as f:
        response = f.read()
    return response


def get_start_date(res='Daily'):
    if res == 'Daily': return now() - timedelta(days=2)
    elif res == 'Weekly': return now() - timedelta(days=14)
    elif res == 'Monthly': return now() - timedelta(days=60)
    elif res == 'Yearly': return now() - timedelta(days=400)
    else: raise ValueError
    return start_date
