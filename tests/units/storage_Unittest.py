#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import unittest2 as unittest
import os
import sys
import time
import socket
import rrdtool
import mock

myPath = os.path.abspath(os.path.dirname(__file__))

sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../../common'))
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../../storage/module'))

#from numeter_storage import myStorage
import numeter_storage
#from myRedisConnect import myRedisConnect
#import myRedisConnect

import base as test_base
from test_utils import FakeRedis

class StorageTestCase(test_base.TestCase):

    def setUp(self):
        super(StorageTestCase, self).setUp()
        self.getgloballog_orig = numeter_storage.myStorage.getgloballog
        numeter_storage.myStorage.getgloballog = mock.MagicMock()
        self.storage = numeter_storage.myStorage(myPath+"/storage_unittest.cfg")
        self.storage._logger = myFakeLogger()

    def tearDown(self):
        super(StorageTestCase, self).tearDown()
        numeter_storage.myStorage.getgloballog = numeter_storage.myStorage.getgloballog

    def test_storage_getcollectorList_file(self):
        self.storage._collector_list_type = "file" 
        self.storage._collector_list_file = "/tmp/collectorList.unittest"
        with mock.patch('__builtin__.open', mock.mock_open(), create=True) as file_mock:
            # Test with Empty file
            file_mock.return_value.readlines.return_value = []
            self.storage.getcollectorList()
            self.assertEqual(self.storage._collectorList, [])
            # Empty line
            file_mock.return_value.readlines.return_value = ['','']
            self.storage.getcollectorList()
            self.assertEqual(self.storage._collectorList, [])
            # Test with 3 hostname and one db and password
            file_mock.return_value.readlines.return_value = ['foo','bar:1', 'bli:2:pwd']
            self.storage.getcollectorList()
            self.assertEqual(self.storage._collectorList, [{'host': 'foo'},
                                                           {'db': '1', 'host': 'bar'},
                                                           {'db': '2', 'host': 'bli', 'password': 'pwd'}])
            # Test with hostname + bad db
            file_mock.return_value.readlines.return_value = ['foo:db1']
            self.storage.getcollectorList()
            self.assertEqual(self.storage._collectorList, [])
            # One host + comment
            file_mock.return_value.readlines.return_value = ['# my host','foo']
            self.storage.getcollectorList()
            self.assertEqual(self.storage._collectorList, [{'host': 'foo'}])
            # clear \s after hostname
            file_mock.return_value.readlines.return_value = ['foo   :0']
            self.storage.getcollectorList()
            self.assertEqual(self.storage._collectorList, [{'host': 'foo', 'db': '0'}])

    def test_storage_getData(self):
        # no data
        collectorRedis = FakeRedis()
        (allTS,hostDatas) = self.storage.getData(collectorRedis,'myhost')
        self.assertEqual((allTS,hostDatas), ([], {}))
        # One TS but no datas (clean TS)
        collectorRedis = FakeRedis()
        collectorRedis.redis_zadd("TS@myhost",'1000000000',1000000000)
        (allTS,hostDatas) = self.storage.getData(collectorRedis,'myhost')
        self.assertEqual((allTS,hostDatas), ([], {}))
        result = collectorRedis.redis_zrangebyscore("TS@myhost",'-inf','+inf')
        self.assertEqual(result, [])
        # Fetch data and delete older data with no TS
        collectorRedis = FakeRedis()
        collectorRedis.redis_zadd("TS@myhost",'1000000001',1000000001)
        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000000","Values":{"old": "0"}}',1000000000)
        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000001","Values":{"new": "0"}}',1000000001)
        (allTS,hostDatas) = self.storage.getData(collectorRedis,'myhost')
        self.assertEqual((allTS,hostDatas), (['1000000001'], {u'foo': {u'1000000001': {u'new': u'0'}}}))
        result = collectorRedis.redis_zrangebyscore("DATAS@myhost",'-inf','+inf')
        self.assertEqual(result, ['{"Plugin":"foo","TimeStamp":"1000000001","Values":{"new": "0"}}']) # Clean old datas
        # Fetch data and don't fetch or delete new data without TS, clean old datas without TS
        collectorRedis = FakeRedis()
        collectorRedis.redis_zadd("TS@myhost",'1000000001',1000000001)
        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000000","Values":{"old": "0"}}',1000000000)
        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000001","Values":{"curr": "0"}}',1000000001)
        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000002","Values":{"new": "0"}}',1000000002)
        (allTS,hostDatas) = self.storage.getData(collectorRedis,'myhost')
        self.assertEqual((allTS,hostDatas), (['1000000001'], {u'foo': {u'1000000001': {u'curr': u'0'}}}))
        result = collectorRedis.redis_zrangebyscore("DATAS@myhost",'-inf','+inf')
        self.assertEqual(result, ['{"Plugin":"foo","TimeStamp":"1000000001","Values":{"curr": "0"}}',
                                  '{"Plugin":"foo","TimeStamp":"1000000002","Values":{"new": "0"}}']) # Clean old datas
        # Fetch bad data and dont stock them
        collectorRedis = FakeRedis()
        collectorRedis.redis_zadd("TS@myhost",'1000000001',1000000001)
        collectorRedis.redis_zadd("TS@myhost",'1000000002',1000000002)
        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000001","Values":{"curr": "0"}}',1000000001)
        collectorRedis.redis_zadd("DATAS@myhost",'{"Values":{"new": "0"}}',1000000002)
        (allTS,hostDatas) = self.storage.getData(collectorRedis,'myhost')
        self.assertEqual((allTS,hostDatas), (['1000000001', '1000000002'], {u'foo': {u'1000000001': {u'curr': u'0'}}}))
        # 2 data available and max_data_by_hosts are 1, so get only one data
        collectorRedis = FakeRedis()
        self.storage._max_data_by_hosts = 1
        collectorRedis.redis_zadd("TS@myhost",'1000000001',1000000001)
        collectorRedis.redis_zadd("TS@myhost",'1000000002',1000000002)
        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000001","Values":{"curr": "0"}}',1000000001)
        collectorRedis.redis_zadd("DATAS@myhost",'{"Plugin":"foo","TimeStamp":"1000000002","Values":{"new": "0"}}',1000000002)
        (allTS,hostDatas) = self.storage.getData(collectorRedis,'myhost')
        self.assertEqual((allTS,hostDatas), (['1000000001'], {u'foo': {u'1000000001': {u'curr': u'0'}}}))


    def test_storage_getHostList(self):
        # Empty HOSTS in redis
        with mock.patch('numeter_storage.myRedisConnect', FakeRedis) as redis:
            collectorLine = {'host': '127.0.0.1', 'password': 'password', 'db': '1'}
            hostList = self.storage.getHostList(collectorLine)
            self.assertEqual(hostList, [])
        # 2 hosts
        with mock.patch('numeter_storage.myRedisConnect', FakeRedis) as redis:
            initdb = redis()
            initdb.redis_hset('HOSTS', 'host1', 'bar')
            initdb.redis_hset('HOSTS', 'host2', 'foo')
            init_hset_back = redis.init_hset
            def init_db(self):
                return initdb.hset_data
            redis.init_hset = init_db
            collectorLine = {'host': '127.0.0.1', 'password': 'password', 'db': '1'}
            hostList = self.storage.getHostList(collectorLine)
            self.assertEqual(hostList, ['foo', 'bar'])
            redis.init_hset = init_hset_back


    def test_storage_getInfos(self):
        # Fake storage db
        self.storage._redis_connexion = FakeRedis()
        self.storage._rrd_path_md5_char = 2
        # Fake collector db
        self.storage._redis_storage_db = 1
        # No Infos
        collector_db = FakeRedis()
        (writedinfo, result, rrdPath) = self.storage.getInfos(collector_db,'myhost')
        self.assertEqual(result, {})
        self.assertEqual(writedinfo, [])
        # One good info + MyInfo plugin
        collector_db = FakeRedis()
        foo = '{"Plugin": "foo", "Infos": { "bar":{"id": "bar"}, "gnu":{"type": "COUNTER", "id": "gnu"}}}'
        MyInfo = '{ "Plugin": "MyInfo", "ID": "myhost", "Name": "myhostName"}'
        collector_db.redis_hset('INFOS@myhost', 'foo', foo)
        collector_db.redis_hset('INFOS@myhost', 'MyInfo', MyInfo)
        (writedinfo, result, rrdPath) = self.storage.getInfos(collector_db, 'myhost')
        self.assertEqual(result, {'MyInfo': {u'Name': u'myhostName', 'HostIDHash': 'cc', u'ID': u'myhost', 'HostIDFiltredName': u'myhost', u'Plugin': u'MyInfo'}, 'foo': {u'Infos': {u'bar': {u'id': u'bar'}, u'gnu': {u'type': u'COUNTER', u'id': u'gnu'}}, u'Plugin': u'foo'}} )
        self.assertEqual(writedinfo, ['foo', 'MyInfo'])
        # Only myinfo.
        collector_db = FakeRedis()
        MyInfo = '{ "Plugin": "MyInfo", "ID": "myhost", "Name": "myhostName"}'
        collector_db.redis_hset("INFOS@myhost", "MyInfo", MyInfo)
        (writedinfo, result, rrdPath) = self.storage.getInfos(collector_db, 'myhost')
        self.assertEqual(result, {'MyInfo': {u'Name': u'myhostName', 'HostIDHash': 'cc', u'ID': u'myhost', 'HostIDFiltredName': u'myhost', u'Plugin': u'MyInfo'}} )
        # Plugin with no Infos so return only MyInfo
        collector_db = FakeRedis()
        MyInfo = '{ "Plugin": "MyInfo", "ID": "myhost", "Name": "myhostName"}'
        foo = '{"Plugin": "foo"}'
        collector_db.redis_hset("INFOS@myhost","foo",foo)
        collector_db.redis_hset("INFOS@myhost","MyInfo",MyInfo)
        (writedinfo, result, rrdPath) = self.storage.getInfos(collector_db,'myhost')
        self.assertEqual(result, {'MyInfo': {u'Name': u'myhostName', 'HostIDHash': 'cc', u'ID': u'myhost', 'HostIDFiltredName': u'myhost', u'Plugin': u'MyInfo'}} )
        self.assertEqual(writedinfo, ['MyInfo'])
        # No MyInfo so return {} (can't write rrd)
        collector_db = FakeRedis()
        foo = '{"Plugin": "foo", "Infos": {}}'
        collector_db.redis_hset("INFOS@myhost","foo",foo)
        (writedinfo, result, rrdPath) = self.storage.getInfos(collector_db,'myhost')
        self.assertEqual(result, {} )
        self.assertEqual(writedinfo, [])
        # Test hostid name filter
        collector_db = FakeRedis()
        foo = '{"Plugin": "foo", "Infos": {}}'
        MyInfo = '{"Name": "myhostName", "Plugin": "MyInfo", "ID": "myhost"}'
        collector_db.redis_hset("INFOS@myhost","MyInfo",MyInfo)
        (writedinfo, result, rrdPath) = self.storage.getInfos(collector_db,'myhost')
        self.assertEqual(result["MyInfo"]["HostIDFiltredName"], "myhost" )
        MyInfo = '{"Name": "myhostName", "Plugin": "MyInfo", "ID": "my\'host"}'
        collector_db.redis_hset("INFOS@myhost","MyInfo",MyInfo)
        (writedinfo, result, rrdPath) = self.storage.getInfos(collector_db,'myhost')
        self.assertEqual(result["MyInfo"]["HostIDFiltredName"], "myhost" )
        MyInfo = '{ "Plugin": "MyInfo", "ID": "Foo bar", "Name": "myhostName"}'
        collector_db.redis_hset("INFOS@myhost","MyInfo",MyInfo)
        (writedinfo, result, rrdPath) = self.storage.getInfos(collector_db,'myhost')
        self.assertEqual(result["MyInfo"]["HostIDFiltredName"], "Foobar" )
        MyInfo = '{ "Plugin": "MyInfo", "ID": "Foo\\"bar", "Name": "myhostName"}'
        collector_db.redis_hset("INFOS@myhost","MyInfo",MyInfo)
        (writedinfo, result, rrdPath) = self.storage.getInfos(collector_db,'myhost')
        self.assertEqual(result["MyInfo"]["HostIDFiltredName"], "Foobar" )
        # Test md5 sum
        collector_db = FakeRedis()
        self.storage._redis_connexion = FakeRedis()
        self.storage._rrd_path_md5_char = 32
        MyInfo = '{ "Plugin": "MyInfo", "ID": "foobar", "Name": "myhostName"}'
        collector_db.redis_hset("INFOS@myhost","MyInfo",MyInfo)
        (writedinfo, result, rrdPath) = self.storage.getInfos(collector_db,'myhost')
        self.assertEqual(result["MyInfo"]["HostIDHash"], "3858f62230ac3c915f300c664312c63f" )
        # Test md5 rrd_path_md5_char
        collector_db = FakeRedis()
        self.storage._redis_connexion = FakeRedis()
        self.storage._rrd_path_md5_char = 5
        MyInfo = '{ "Plugin": "MyInfo", "ID": "foobar", "Name": "myhostName"}'
        collector_db.redis_hset("INFOS@myhost","MyInfo",MyInfo)
        (writedinfo, result, rrdPath) = self.storage.getInfos(collector_db,'myhost')
        self.assertEqual(result["MyInfo"]["HostIDHash"], "3858f" )
        # Try to read in cache
        collector_db = FakeRedis()
        self.storage._redis_connexion = FakeRedis()
        MyInfo = '{ "Plugin": "MyInfo", "ID": "foobar", "Name": "myhostName"}'
        collector_db.redis_hset("INFOS@myhost","MyInfo",MyInfo)
        result = self.storage._redis_connexion.redis_hset("HOST_ID","foobar","42")
        (writedinfo, result, rrdPath) = self.storage.getInfos(collector_db,'myhost')
        self.assertEqual(result["MyInfo"]["HostIDHash"], "42")
        # Test rrd path fot host
        collector_db = FakeRedis()
        self.storage._redis_connexion = FakeRedis()
        self.storage._rrd_path_md5_char = 2
        MyInfo = '{ "Plugin": "MyInfo", "ID": "myhost", "Name": "myhostName"}'
        collector_db.redis_hset("INFOS@myhost","MyInfo",MyInfo)
        self.storage.getInfos(collector_db,'myhost')
        result = self.storage._redis_connexion.redis_hget("RRD_PATH","myhost")
        self.assertEqual(result, "/tmp/numeter_rrds/cc/myhost")


# Need to be rewrited with whisper
#    def test_sorage_cleanInfo(self):
#
#    def test_sorage_cleanHosts(self):
#
#    def test_storage_writeRrdtool(self):
#
#    def test_storage_workerRedis(self):
#
#    def test_storage_cleanOldRRD(self):


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
