#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import time
import socket

myPath = os.path.abspath(os.path.dirname(__file__))

sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/../../collector/module'))
from numeter_collector import *

class CollectorTestCase(unittest.TestCase):


    def setUp(self):
        os.system("kill $(cat /tmp/redis-unittest.pid 2>/dev/null) 2>/dev/null")
        os.system('kill -9 $(pgrep -f "redis-server '+myPath+'/redis_unittest.conf")')
        os.system("redis-server "+myPath+"/redis_unittest.conf")
        os.system("while ! netstat -laputn | grep 8888 > /dev/null; do true; done ")
        os.system("redis-cli -a password -p 8888 ping >/dev/null")
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        self.collector = myCollector(myPath+"/collector_unittest.cfg")
        self.collector._logger = myFakeLogger()

    def tearDown(self):
        os.system("kill -9 $(cat /tmp/redis-unittest.pid)")
        os.system('kill -9 $(pgrep -f "redis-server '+myPath+'/redis_unittest.conf")')

    def test_collector_getHostsList_file(self):
        self.collector._host_list_type = "file" 
        self.collector._host_list_file = "/tmp/hostList.unittest"
        # Test with no file
        os.system("rm -f "+self.collector._host_list_file)
        self.assertRaises(SystemExit, self.collector.getHostsList)
        # Test with Empty file
        os.system(":> "+self.collector._host_list_file)
        self.collector.getHostsList()
        self.assertEqual(self.collector._hostList, [])
        # Empty line
        os.system('echo "\n\n\n" > '+self.collector._host_list_file)
        self.collector.getHostsList()
        self.assertEqual(self.collector._hostList, [])
        # Test with one hostname
        os.system("echo 'foo' > "+self.collector._host_list_file)
        self.collector.getHostsList()
        self.assertEqual(self.collector._hostList, [{'host': 'foo'}])
        # Test with 2 hostname
        os.system('echo "foo\nbar" > '+self.collector._host_list_file)
        self.collector.getHostsList()
        self.assertEqual(self.collector._hostList, [{'host': 'foo'}, {'host': 'bar'}])
        # Test with hostname + good db
        os.system("echo 'foo:0' >"+self.collector._host_list_file)
        self.collector.getHostsList()
        self.assertEqual(self.collector._hostList, [{'host': 'foo', 'db': '0'}])
        # Test with hostname + bad db
        os.system("echo 'foo:db0' >"+self.collector._host_list_file)
        self.collector.getHostsList()
        self.assertEqual(self.collector._hostList, [])
        # Test with hostname + good db + passwd
        os.system("echo 'foo:0:password' >"+self.collector._host_list_file)
        self.collector.getHostsList()
        self.assertEqual(self.collector._hostList, [{'host': 'foo', 'password': 'password', 'db': '0'}])
        # Test 3 host + 2 db + 1 password
        os.system("echo 'foo\nbar:1\nbli:2:p' >"+self.collector._host_list_file)
        self.collector.getHostsList()
        self.assertEqual(self.collector._hostList, [{'host': 'foo',},
                                                    {'host': 'bar', 'db': '1'},
                                                    {'host': 'bli', 'password': 'p', 'db': '2'}])
        # One host + comment
        os.system('echo "foo\n#bar" > '+self.collector._host_list_file)
        self.collector.getHostsList()
        self.assertEqual(self.collector._hostList, [{'host': 'foo'}])
        # One bad hostname (space)
        os.system('echo "foo bar" > '+self.collector._host_list_file)
        self.collector.getHostsList()
        self.assertEqual(self.collector._hostList, [])
        # One bad hostname with space after
        os.system('echo "foobar     " > '+self.collector._host_list_file)
        self.collector.getHostsList()
        self.assertEqual(self.collector._hostList, [{'host': 'foobar'}])
        # Only host with space after + db with space after
        os.system('echo "foobar     :0     " > '+self.collector._host_list_file)
        self.collector.getHostsList()
        self.assertEqual(self.collector._hostList, [{'host': 'foobar', 'db': '0'}])
        # Only host + db + space after + passwrd
        os.system('echo "foobar     :0     :p" > '+self.collector._host_list_file)
        self.collector.getHostsList()
        self.assertEqual(self.collector._hostList, [{'host': 'foobar', 'password': 'p', 'db': '0'}])


    def test_collector_redisStartConnexion(self):
        # Connect with 0
        self.collector._redis_server_db = 0
        zeroConnect = self.collector.redisStartConnexion()
        zeroConnect.redis_hset("DB","foo","bar0")
        # Connect with 1
        self.collector._redis_server_db = 1
        oneConnect = self.collector.redisStartConnexion()
        oneConnect.redis_hset("DB","foo","bar1")
        # Check
        result = zeroConnect.redis_hget("DB","foo")
        self.assertEquals(result, "bar0")
        result = oneConnect.redis_hget("DB","foo")
        self.assertEquals(result, "bar1")



    def test_collector_workerGetLastFetch(self):
        # Start connexion client (db0)
        self.collector._redis_server_db = 0
        pollerRedis = self.collector.redisStartConnexion()
        # Never fetch and no data
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        (last,end) = self.collector.workerGetLastFetch(pollerRedis,'1','myhost')
        self.assertEqual((last,end), (None,None))
        # Never fetch and one data
        pollerRedis.redis_zadd("TimeStamp",'1000000000',1000000000)
        (last,end) = self.collector.workerGetLastFetch(pollerRedis,'1','myhost')
        self.assertEqual((last,end), ('-inf', '1000000000'))
        # Already fetch and no new data
        pollerRedis.redis_hset("SERVER",'unittest',1000000000)
        pollerRedis.redis_zadd("TimeStamp",'1000000000',1000000000)
        (last,end) = self.collector.workerGetLastFetch(pollerRedis,'1','myhost')
        self.assertEqual((last,end), (None, None))
        # Already fetch and one new data
        pollerRedis.redis_hset("SERVER",'unittest',1000000000)
        pollerRedis.redis_zadd("TimeStamp",'1000000000',1000000000)
        pollerRedis.redis_zadd("TimeStamp",'1000000001',1000000001)
        (last,end) = self.collector.workerGetLastFetch(pollerRedis,'1','myhost')
        self.assertEqual((last,end), ('1000000000', '1000000001'))
        # Already fetch Max fetch data = 2 and add 3 data available
        pollerRedis.redis_hset("SERVER",'unittest',1000000000)
        pollerRedis.redis_zadd("TimeStamp",'1000000000',1000000000)
        pollerRedis.redis_zadd("TimeStamp",'1000000001',1000000001)
        pollerRedis.redis_zadd("TimeStamp",'1000000002',1000000002)
        pollerRedis.redis_zadd("TimeStamp",'1000000003',1000000003)
        (last,end) = self.collector.workerGetLastFetch(pollerRedis,'1','myhost')
        self.assertEqual((last,end), ('1000000000', '1000000002'))
        # Never fetch Max fetch data = 2 and add 3 data available
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        pollerRedis.redis_zadd("TimeStamp",'1000000000',1000000000)
        pollerRedis.redis_zadd("TimeStamp",'1000000001',1000000001)
        pollerRedis.redis_zadd("TimeStamp",'1000000002',1000000002)
        (last,end) = self.collector.workerGetLastFetch(pollerRedis,'1','myhost')
        self.assertEqual((last,end), ('-inf', '1000000001'))


    def test_collector_workerFetchDatas(self):
        # Start connexion poller (db0)
        self.collector._redis_server_db = 0
        pollerRedis = self.collector.redisStartConnexion()
        # Start connexion poller (db1)
        self.collector._redis_server_db = 1
        collectorRedis = self.collector.redisStartConnexion()
        self.collector._redis_connection = collectorRedis
        # Never fetch and no data
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        result = self.collector.workerFetchDatas(pollerRedis,'1','myhost','123456',None,None)
        self.assertEqual(result, False)
        # Never fetch but no data
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        self.collector.workerFetchDatas(pollerRedis,'1','myhost','123456','-inf','1000000000')
        result = collectorRedis.redis_zrangebyscore("DATAS@123456",'-inf','+inf')
        self.assertEqual(result, [])
        # empty data
        pollerRedis.redis_zadd("DATAS",'',1000000000)
        self.collector.workerFetchDatas(pollerRedis,'1','myhost','123456','-inf','+inf')
        result = collectorRedis.redis_zrangebyscore("DATAS@123456",'-inf','+inf')
        self.assertEqual(result, [])
        # bad json data
        pollerRedis.redis_zadd("DATAS",'',1000000000)
        self.collector.workerFetchDatas(pollerRedis,'1','myhost','123456','-inf','+inf')
        result = collectorRedis.redis_zrangebyscore("DATAS@123456",'-inf','+inf')
        self.assertEqual(result, [])
        # Data without Plugin field
        pollerRedis.redis_zadd("DATAS",'{"Plugin":"foo"}',1000000000)
        self.collector.workerFetchDatas(pollerRedis,'1','myhost','123456','-inf','+inf')
        result = collectorRedis.redis_zrangebyscore("DATAS@123456",'-inf','+inf')
        self.assertEqual(result, [])
        # Data with bad timestamp
        pollerRedis.redis_zadd("DATAS",'{"Plugin":"foo","TimeStamp":"a","Values":"bar"}',1000000000)
        self.collector.workerFetchDatas(pollerRedis,'1','myhost','123456','-inf','+inf')
        result = collectorRedis.redis_zrangebyscore("DATAS@123456",'-inf','+inf')
        self.assertEqual(result, [])
        # good Data
        pollerRedis.redis_zadd("DATAS",'{"Plugin":"foo","TimeStamp":"1000000000","Values":"bar"}',1000000000)
        self.collector.workerFetchDatas(pollerRedis,'1','myhost','123456','-inf','+inf')
        result = collectorRedis.redis_zrangebyscore("DATAS@123456",'-inf','+inf')
        self.assertEqual(result, ['{"Plugin":"foo","TimeStamp":"1000000000","Values":"bar"}'])
        # Contain already fetched data and new data more than limit
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        pollerRedis.redis_zadd("DATAS",'{"Plugin":"foo","TimeStamp":"1000000000","Values":"bar"}',1000000000)
        pollerRedis.redis_zadd("DATAS",'{"Plugin":"foo","TimeStamp":"1000000001","Values":"bar"}',1000000001)
        pollerRedis.redis_zadd("DATAS",'{"Plugin":"foo","TimeStamp":"1000000002","Values":"bar"}',1000000002)
        self.collector.workerFetchDatas(pollerRedis,'1','myhost','123456','1000000000', '1000000001')
        result = collectorRedis.redis_zrangebyscore("DATAS@123456",'-inf','+inf')
        self.assertEqual(result, ['{"Plugin":"foo","TimeStamp":"1000000001","Values":"bar"}'])
        # Never fetch get just one data
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        pollerRedis.redis_zadd("DATAS",'{"Plugin":"foo","TimeStamp":"1000000000","Values":"bar"}',1000000000)
        pollerRedis.redis_zadd("DATAS",'{"Plugin":"foo","TimeStamp":"1000000001","Values":"bar"}',1000000001)
        self.collector.workerFetchDatas(pollerRedis,'1','myhost','123456','-inf', '1000000000')
        result = collectorRedis.redis_zrangebyscore("DATAS@123456",'-inf','+inf')
        self.assertEqual(result, ['{"Plugin":"foo","TimeStamp":"1000000000","Values":"bar"}'])
        result = collectorRedis.redis_hgetall("HOSTS")
        self.assertEqual(result, {'myhost': '123456'})

    def test_collector_workerFetchInfos(self):
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        # Start connexion poller (db0)
        self.collector._redis_server_db = 0
        pollerRedis = self.collector.redisStartConnexion()
        # Start connexion poller (db1)
        self.collector._redis_server_db = 1
        collectorRedis = self.collector.redisStartConnexion()
        self.collector._redis_connection = collectorRedis
        # No infos
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        result = self.collector.workerFetchInfos(pollerRedis,'1','myhost')
        self.assertEqual(result, ([], None))
        # good infos
        pollerRedis.redis_hset("INFOS",'MyInfo','{"ID": "123456"}')
        pollerRedis.redis_hset("INFOS",'bar','{bla}')
        result, result2 = self.collector.workerFetchInfos(pollerRedis,'1','myhost')
        self.assertEqual(result, ['MyInfo', 'bar'])
        self.assertEqual(result2, "123456")
        result = collectorRedis.redis_hgetall("INFOS@123456")
        self.assertEqual(result, {'MyInfo': '{"ID": "123456", "Address": "myhost"}', 'bar': '{bla}'})

    def test_collector_workerRedis(self):
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        # Start connexion poller (db0)
        self.collector._redis_server_db = 0
        pollerRedis = self.collector.redisStartConnexion()
        # Start connexion poller (db1)
        self.collector._redis_server_db = 1
        collectorRedis = self.collector.redisStartConnexion()
        self.collector._redis_connection = collectorRedis
        sema = myFakeSema()
        # Init workerFetchDatas
        pollerRedis.redis_zadd("TimeStamp",'1000000000',1000000000)
        pollerRedis.redis_zadd("DATAS",'{"Plugin":"foo","TimeStamp":"1000000000","Values": {"bar": "42"}}',1000000000)
        # Init workerFetchInfos
        pollerRedis.redis_hset("INFOS",'foo','{"Describ": "", "Title": "foo_test", "Plugin": "foo", "Infos": {"foo": {"id": "foo"}}}')
        pollerRedis.redis_hset("INFOS",'MyInfo','{"ID": "123456"}')
        # Start worker
        self.collector.workerRedis(1, sema,[{'host': '127.0.0.1', 'password': 'password', 'db': '0'}])
        result = collectorRedis.redis_hgetall("INFOS@123456")
        self.assertEqual(result, {'MyInfo': '{"ID": "123456", "Address": "127.0.0.1"}', 'foo': '{"Describ": "", "Title": "foo_test", "Plugin": "foo", "Infos": {"foo": {"id": "foo"}}}'})
        result = collectorRedis.redis_zrangebyscore("DATAS@123456",'-inf','+inf')
        self.assertEqual(result, ['{"Plugin":"foo","TimeStamp":"1000000000","Values": {"bar": "42"}}'])

    def test_collector_workerCleanInfo(self):
        self.collector._redis_connection = self.collector.redisStartConnexion()
        collectorRedis = self.collector._redis_connection
        host = 'myhost'
        threadId = 1
        # No data before (dont delete no data after)
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        self.collector.workerCleanInfo(["foo","bar"], host, threadId)
        result = collectorRedis.redis_hkeys("INFOS")
        self.assertEquals(result, [])
        # 2 data before and same data now
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        collectorRedis.redis_hset("INFOS@"+host,'foo','foo')
        collectorRedis.redis_hset("INFOS@"+host,'bar','bar')
        self.collector.workerCleanInfo(["foo","bar"], host, threadId)
        result = collectorRedis.redis_hkeys("INFOS@"+host)
        self.assertEquals(result, ['foo', 'bar'])
        # 2 data before and only one now
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        collectorRedis.redis_hset("INFOS@"+host,'foo','foo')
        collectorRedis.redis_hset("INFOS@"+host,'bar','bar')
        self.collector.workerCleanInfo(["foo"], host, threadId)
        result = collectorRedis.redis_hkeys("INFOS@"+host)
        self.assertEquals(result, ['foo'])
        # 2 data before and 2 new
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        collectorRedis.redis_hset("INFOS@"+host,'foo','foo')
        collectorRedis.redis_hset("INFOS@"+host,'bar','bar')
        self.collector.workerCleanInfo(["gnu","bli"], host, threadId)
        result = collectorRedis.redis_hkeys("INFOS@"+host)
        self.assertEquals(result, [])
        # 2 data before and old + 2 new now
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        collectorRedis.redis_hset("INFOS@"+host,'foo','foo')
        collectorRedis.redis_hset("INFOS@"+host,'bar','bar')
        self.collector.workerCleanInfo(["foo","bar","gnu","bli"], host, threadId)
        result = collectorRedis.redis_hkeys("INFOS@"+host)
        self.assertEquals(result, ['foo', 'bar'])
        # 2 data before and 1 old delete and one new now
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        collectorRedis.redis_hset("INFOS@"+host,'foo','foo')
        collectorRedis.redis_hset("INFOS@"+host,'bar','bar')
        self.collector.workerCleanInfo(["foo","gnu"], host, threadId)
        result = collectorRedis.redis_hkeys("INFOS@"+host)
        self.assertEquals(result, ['foo'])

    def test_collector_cleanHosts(self):
        self.collector._redis_connection = self.collector.redisStartConnexion()
        collectorRedis = self.collector._redis_connection
        # Nothing before
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        self.collector._hostList = [{'host': 'foo'},{'host': 'bar'}]
        self.collector.cleanHosts()
        result = collectorRedis.redis_hkeys("HOSTS")
        self.assertEquals(result, [])
        # Same host
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        collectorRedis.redis_hset("INFOS@foo",'df','df')
        collectorRedis.redis_zadd("DATAS@foo",'somedata',1000000000)
        collectorRedis.redis_hset("HOSTS",'foo','foo')
        self.collector._hostList = [{'host': 'foo'}]
        self.collector.cleanHosts()
        result = collectorRedis.redis_hkeys("HOSTS")
        self.assertEquals(result, ['foo'])
        result = collectorRedis.redis_hkeys("INFOS@foo")
        self.assertEquals(result, ['df'])
        result = collectorRedis.redis_zrangebyscore("DATAS@foo",'-inf','+inf')
        self.assertEquals(result, ['somedata'])
        # One new host
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        collectorRedis.redis_hset("INFOS@foo",'df','df')
        collectorRedis.redis_zadd("DATAS@foo",'somedata',1000000000)
        collectorRedis.redis_hset("HOSTS",'foo','foo')
        self.collector._hostList = [{'host': 'foo'},{'host': 'bar'}]
        self.collector.cleanHosts()
        result = collectorRedis.redis_hkeys("HOSTS")
        self.assertEquals(result, ['foo'])
        result = collectorRedis.redis_hkeys("INFOS@foo")
        self.assertEquals(result, ['df'])
        result = collectorRedis.redis_zrangebyscore("DATAS@foo",'-inf','+inf')
        self.assertEquals(result, ['somedata'])
        # 2 host before and delete one now
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        for host in ['foo','bar']:
            collectorRedis.redis_hset("INFOS@"+host,'df','df')
            collectorRedis.redis_hset("INFOS@"+host,'if','if')
            collectorRedis.redis_zadd("DATAS@"+host,'somedata',1000000000)
            collectorRedis.redis_hset("HOSTS",host,host)
        self.collector._hostList = [{'host': 'foo'}]
        self.collector.cleanHosts()
        result = collectorRedis.redis_hkeys("HOSTS")
        self.assertEquals(result, ['foo'])
        result = collectorRedis.redis_hkeys("INFOS@foo")
        self.assertEquals(result, ['df','if'])
        result = collectorRedis.redis_zrangebyscore("DATAS@foo",'-inf','+inf')
        self.assertEquals(result, ['somedata'])
        result = collectorRedis.redis_zrangebyscore("DATAS@bar",'-inf','+inf')
        self.assertEquals(result, [])
        result = collectorRedis.redis_hkeys("INFOS@bar")
        self.assertEquals(result, [])
        # 2 host before and delete old + add 2 new
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        for host in ['foo','bar']:
            collectorRedis.redis_hset("INFOS@"+host,'df','df')
            collectorRedis.redis_hset("INFOS@"+host,'if','if')
            collectorRedis.redis_zadd("DATAS@"+host,'somedata',1000000000)
            collectorRedis.redis_hset("HOSTS",host,host)
        self.collector._hostList = [{'host': 'gnu'},{'host': 'bli'}]
        self.collector.cleanHosts()
        result = collectorRedis.redis_hkeys("HOSTS")
        self.assertEquals(result, [])
        result = collectorRedis.redis_hkeys("INFOS@foo")
        self.assertEquals(result, [])
        result = collectorRedis.redis_zrangebyscore("DATAS@foo",'-inf','+inf')
        self.assertEquals(result, [])
        result = collectorRedis.redis_zrangebyscore("DATAS@bar",'-inf','+inf')
        self.assertEquals(result, [])
        result = collectorRedis.redis_hkeys("INFOS@bar")
        self.assertEquals(result, [])
        # 2 host before + add 2 new
        os.system("redis-cli -a password -p 8888 FLUSHALL >/dev/null")
        for host in ['foo','bar']:
            collectorRedis.redis_hset("INFOS@"+host,'df','df')
            collectorRedis.redis_hset("INFOS@"+host,'if','if')
            collectorRedis.redis_zadd("DATAS@"+host,'somedata',1000000000)
            collectorRedis.redis_hset("HOSTS",host,host)
        self.collector._hostList = [{'host': 'foo'},{'host': 'bar'},{'host': 'gnu'},{'host': 'bli'}]
        self.collector.cleanHosts()
        result = collectorRedis.redis_hkeys("HOSTS")
        self.assertEquals(result, ['foo','bar'])
        result = collectorRedis.redis_hkeys("INFOS@foo")
        self.assertEquals(result, ['df','if'])
        result = collectorRedis.redis_zrangebyscore("DATAS@foo",'-inf','+inf')
        self.assertEquals(result, ['somedata'])
        result = collectorRedis.redis_zrangebyscore("DATAS@bar",'-inf','+inf')
        self.assertEquals(result, ['somedata'])
        result = collectorRedis.redis_hkeys("INFOS@bar")
        self.assertEquals(result, ['df','if'])





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
# Fake sema
class myFakeSema():
    def __init__(self):
        return
    def release(self):
        return






