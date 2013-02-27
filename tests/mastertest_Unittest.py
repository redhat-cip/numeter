#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import time
import socket
import re
import subprocess
import rrdtool


# Need munin-node redis-server

myPath = os.path.abspath(os.path.dirname(__file__))

sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../poller/module'))
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../common/module'))
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../storage/module'))
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../collector/module'))

from numeter_poller import *
from numeter_collector import *
from numeter_storage import *

#foo_unittest|bar_unittest
class MasterTestCase(unittest.TestCase):

    def get_init_munin(self):
        # Start munin
        process = subprocess.Popen(myPath+"/mastertest_makeMuninScript.sh", shell=True, stdout=subprocess.PIPE)
        (result, stderr) =  process.communicate()
        self.assertEquals(result,"True")

    def setUp(self):
        os.system("rm -f /tmp/poller_last.unittest")
        os.system("kill -9 $(cat /var/run/redis/redis-unittest.pid 2>/dev/null) 2>/dev/null")
        os.system('kill -9 $(pgrep -f "redis-server '+myPath+'/redis_unittest.conf")')
        os.system("redis-server "+myPath+"/redis_unittest.conf")
        os.system("while ! netstat -laputn | grep 8888 > /dev/null; do true; done ")
        os.system("redis-cli -a password -p 8888 ping >/dev/null")
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        self.get_init_munin()


    def tearDown(self):
        os.system("kill -9 $(cat /var/run/redis/redis-unittest.pid)")
        os.system('kill -9 $(pgrep -f "redis-server '+myPath+'/redis_unittest.conf")')
        os.system("rm -f /etc/munin/plugins/bar_unittest")
        os.system("rm -f /etc/munin/plugins/foo_unittest")
        os.system("/etc/init.d/munin-node restart >/dev/null 2>/dev/null")
        os.system("rm -f /tmp/poller_last.unittest")

    def test_mastertest_collect(self):
        # Init
        self.poller = myPoller(myPath+"/poller_unittest.cfg")
        self.collector = myCollector(myPath+"/collector_unittest.cfg")
        self.storage = myStorage(myPath+"/storage_unittest.cfg")
        self.collector._logger = myFakeLogger()
        self.poller._logger = myFakeLogger()
        #
        # Poller
        #
        hostname = socket.gethostname()
        hostID   = "123456"
        self.poller.startPoller()
        pollerRedis = self.poller.redisStartConnexion()
        # Check infos keys
        result = pollerRedis.redis_hkeys("INFOS")
        P_KEYS = ['foo_unittest', 'bar_unittest', 'MyInfo']
        self.assertEquals(result,P_KEYS)
        # Check info foo

        result = pollerRedis.redis_hget("INFOS",'foo_unittest')
        P_INFO_foo = '{"Describ": "", "Title": "foo_test", "Plugin": "foo_unittest", "Vlabel": "foo vlabel", "Base": "1000", "Infos": {"foo": {"draw": "AREA", "id": "foo", "label": "foo label"}}, "Order": ""}'
        self.assertEquals(result,P_INFO_foo)
        # Check info bar
        result = pollerRedis.redis_hget("INFOS",'bar_unittest')
        P_INFO_bar = '{"Describ": "", "Title": "bar gnu test", "Plugin": "bar_unittest", "Vlabel": "bar vlabel", "Base": "1024", "Infos": {"bar": {"draw": "LINE", "type": "COUNTER", "id": "bar", "label": "bar label"}, "gnu": {"id": "gnu"}}, "Order": "gnu bar"}'
        self.assertEquals(result,P_INFO_bar)
        # Check info MyInfos
        result = pollerRedis.redis_hget("INFOS",'MyInfo')
        P_INFO_myinfo = '{"Description": "", "ID": "'+hostID+'", "Name": "'+hostname+'", "Plugin": "MyInfo"}'
        C_INFO_myinfo = '{"Address": "127.0.0.1", "Name": "'+hostname+'", "Plugin": "MyInfo", "Description": "", "ID": "'+hostID+'"}'
        self.assertEquals(result,P_INFO_myinfo)
        # Check des TimeStamp
        result = pollerRedis.redis_zrangebyscore("TimeStamp",'-inf','+inf')
        self.assertTrue(re.match("[0-9]+", result[0]))
        P_TS = result[0]
        # Check des datas
        result = pollerRedis.redis_zrangebyscore("DATAS",'-inf','+inf')
        P_DATAS = ['{"TimeStamp": "'+P_TS+'", "Values": {"bar": "-4.2", "gnu": "4.2"}, "Plugin": "bar_unittest"}', '{"TimeStamp": "'+P_TS+'", "Values": {"foo": "42"}, "Plugin": "foo_unittest"}']
        self.assertEquals(result,P_DATAS)
        
        #
        # Collector
        #
        os.system("echo '127.0.0.1:0:password' > /tmp/poller-list.unittest")
        self.collector.startCollector()
        self.collector._redis_server_db = 1
        collectorRedis = self.collector.redisStartConnexion()
        # Check HOSTS
        result = collectorRedis.redis_hkeys("HOSTS")
        self.assertEquals(result,['127.0.0.1'])
        # Check TS@host
        result = collectorRedis.redis_zrangebyscore("TS@"+hostID, '-inf', '+inf')
        self.assertEquals(result,[P_TS])
        # Check DATAS@host
        result = collectorRedis.redis_zrangebyscore("DATAS@"+hostID, '-inf', '+inf')
        self.assertEquals(result,P_DATAS)
        # Check INFOS@host
        result = collectorRedis.redis_hkeys("INFOS@"+hostID)
        self.assertEquals(result,P_KEYS)
        result = collectorRedis.redis_hget("INFOS@"+hostID,"bar_unittest")
        self.assertEquals(result, P_INFO_bar)
        result = collectorRedis.redis_hget("INFOS@"+hostID,"foo_unittest")
        self.assertEquals(result, P_INFO_foo)
        result = collectorRedis.redis_hget("INFOS@"+hostID,"MyInfo")
        self.assertEquals(result, C_INFO_myinfo)

        # Check SERVER TS in poller
        result = pollerRedis.redis_hget("SERVER","unittest")
        self.assertEquals(result,P_TS)

        #
        # Storage
        #
        os.system("rm -Rf /tmp/numeter_rrds")
        os.system("echo '127.0.0.1:1:password' > /tmp/collector-list.unittest")
        self.storage.startStorage()
        self.storage._redis_server_db = 2
        storageRedis = self.storage.redisStartConnexion()
        # Check HOSTS
        S_INFO_myinfo = { hostID: '{"Description": "", "Plugin": "MyInfo", "HostIDHash": "e1", "HostIDFiltredName": "'+hostID+'", "Address": "127.0.0.1", "ID": "'+hostID+'", "Name": "'+hostname+'"}'}
        result = storageRedis.redis_hgetall("HOSTS")
        self.assertEquals(result, S_INFO_myinfo)

        # Check HOST_ID hash
        S_HOST_ID =  {hostID: 'e1'}
        result = storageRedis.redis_hgetall("HOST_ID")
        self.assertEquals(result, S_HOST_ID)
        # Check RRD_PATH
        S_RRD_PATH = {hostID: '/tmp/numeter_rrds/e1/'+hostID} 
        result = storageRedis.redis_hgetall("RRD_PATH")
        self.assertEquals(result, S_RRD_PATH)
        # Check INFOS@host
        result = storageRedis.redis_hkeys("INFOS@"+hostID)
        P_KEYS_without_myinfo = P_KEYS[:]
        P_KEYS_without_myinfo.remove("MyInfo")
        self.assertEquals(result,P_KEYS_without_myinfo)
        result = storageRedis.redis_hget("INFOS@"+hostID,"bar_unittest")
        self.assertEquals(result, P_INFO_bar)
        result = storageRedis.redis_hget("INFOS@"+hostID,"foo_unittest")
        self.assertEquals(result, P_INFO_foo)
        result = storageRedis.redis_hget("HOSTS",hostID)
        self.assertEquals(result, S_INFO_myinfo[hostID])
        # Test rrd write 
        result = os.path.isfile(S_RRD_PATH[hostID]+"/foo_unittest/foo.rrd")
        self.assertTrue(result)
        result = rrdtool.info(S_RRD_PATH[hostID]+"/foo_unittest/foo.rrd")
        self.assertEqual(result['last_update'], int(P_TS))
        self.assertEqual(result['ds[42].last_ds'], "42")
        self.assertEqual(result['ds[42].type'], "GAUGE")
        #
        result = os.path.isfile(S_RRD_PATH[hostID]+"/bar_unittest/gnu.rrd")
        self.assertTrue(result)
        result = os.path.isfile(S_RRD_PATH[hostID]+"/bar_unittest/bar.rrd")
        self.assertTrue(result)
        result = rrdtool.info(S_RRD_PATH[hostID]+"/bar_unittest/gnu.rrd")
        self.assertEqual(result['last_update'], int(P_TS))
        self.assertEqual(result['ds[42].last_ds'], "4.2")
        self.assertEqual(result['ds[42].type'], "GAUGE")
        result = rrdtool.info(S_RRD_PATH[hostID]+"/bar_unittest/bar.rrd")
        self.assertEqual(result['last_update'], int(P_TS))
        self.assertEqual(result['ds[42].last_ds'], "-4.2")
        self.assertEqual(result['ds[42].type'], "COUNTER")
        # Test clear db collecteur
        result = collectorRedis.redis_zrangebyscore("TS@"+hostID,'+inf','+inf')
        self.assertEqual(result, [])
        result = collectorRedis.redis_zrangebyscore("DATAS@"+hostID,'+inf','+inf')
        self.assertEqual(result, [])

    # Delete DS
    # Delete plugin
    # Delete host
    # Delete client
# Delete rrd storage self._rrd_delete

# Fake log
class myFakeLogger():
    def __init__(self):
        return
    def critical(self,string):
        return
    def error(self,string):
        return
    def warning(self,string):
        return
    def info(self,string):
        return
    def debug(self,string):
        return
    def warn(self,string):
        return






