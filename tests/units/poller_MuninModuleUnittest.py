#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import socket
import logging
import ConfigParser

myPath = os.path.abspath(os.path.dirname(__file__))

from numeter.poller import myMuninModule

import base as test_base

class fakereadline():
    def __init__(self):
        self.read_return = None
        self.count = -1
        return
    def set_return(self,lines):
        self.read_return = lines
        self.count = -1
    def readline(self):
        if len(self.read_return) == 0:
            return
        elif self.count < len(self.read_return) - 1:
            self.count = self.count + 1
        return self.read_return[self.count]

# Class fake socket
class myFakeSocket():
    def __init__(self):
        self._fakeReturnPlugin=['']
        self._fakeReturnNode=['']
        self._fakeReturnValue=['']
        self._fakeReturnConfig=['']
        self._fakeReturn=['']
        self._fakereadline = fakereadline()
        return
    def sendall(self,string):
        if re.match('list.*',string):
            self._fakereadline.set_return(self._fakeReturnPlugin)
        elif re.match('nodes.*',string):
            self._fakereadline.set_return(self._fakeReturnNode)
        elif re.match('config.*',string):
            self._fakereadline.set_return(self._fakeReturnConfig)
        else:
            self._fakereadline.set_return(self._fakeReturnValue)
        return
    def close(self):
        pass

class PollerMuninModuleTestCase(test_base.TestCase):

    def setUp(self):
        super(PollerMuninModuleTestCase, self).setUp()
        # Set logger None
        self._logger = logging.getLogger('numeter')
        fh = logging.FileHandler("/dev/null")
        fh.setLevel(logging.CRITICAL)
        self._logger.addHandler(fh)

        # Set parser
        self._configParse = ConfigParser.RawConfigParser()
        self._configParse.read(myPath+"/poller_unittest.cfg")
        # Fake socker
        self._fakeSocket = myFakeSocket()
        # Start
        self._pollerMuninModule = myMuninModule(self._logger,self._configParse)
        self._pollerMuninModule.munin_connection = self._fakeSocket
        self._pollerMuninModule._plugins_enable=".*"
        def fakemunin_connect():
            pass
        self._pollerMuninModule.munin_connect = fakemunin_connect

    def tearDown(self):
        super(PollerMuninModuleTestCase, self).tearDown()


    def test_muninModule_munin_nodes(self):
        # Init fake readline
        self._pollerMuninModule._s = fakereadline()
        self._pollerMuninModule._s.set_return(['.'])
        # Get my hostname
        hostname = socket.gethostname()
        # Send bad fetch default hostname
        self._pollerMuninModule._s.set_return(['foo'])
        result = self._pollerMuninModule.munin_nodes()
        self.assertEqual(result, 'foo')
        # Send space fetch
        self._pollerMuninModule._s.set_return([' ',' ','.'])
        result = self._pollerMuninModule.munin_nodes()
        self.assertEqual(result, None)
        # Send good + space fetch
        self._pollerMuninModule._s.set_return(['foo',' ','.'])
        result = self._pollerMuninModule.munin_nodes()
        self.assertEqual(result, 'foo')
        # Send empty line
        self._pollerMuninModule._s.set_return(['','',''])
        result = self._pollerMuninModule.munin_nodes()
        self.assertEqual(result, None)
        # Send good with all chars
        self._pollerMuninModule._s.set_return(['f.o-o_A9','.'])
        result = self._pollerMuninModule.munin_nodes()
        self.assertEqual(result, 'f.o-o_A9')
        # Send good fetch with comment
        self._pollerMuninModule._s.set_return(['# bar','foo','.'])
        result = self._pollerMuninModule.munin_nodes()
        self.assertEqual(result, 'foo')

    def test_muninModule_getList(self):
        # Init fake readline
        self._pollerMuninModule._s = self._fakeSocket._fakereadline
        # Send correct list
        self._fakeSocket._fakeReturnPlugin = ['plugin1 plugin2 plugin3']
        result = self._pollerMuninModule.munin_list()
        self.assertEqual(result, ['plugin1','plugin2', 'plugin3'])
        # Send bad list
        self._fakeSocket._fakeReturnPlugin = [' foo']
        result = self._pollerMuninModule.munin_list()
        self.assertEqual(result, ['foo'])
        # Send space list with \n
        self._fakeSocket._fakeReturnPlugin = [' ']
        result = self._pollerMuninModule.munin_list()
        self.assertEqual(result, [])
        # Send space list
        self._fakeSocket._fakeReturnPlugin = ['  ']
        result = self._pollerMuninModule.munin_list()
        self.assertEqual(result, [])
        # Send valid list
        self._fakeSocket._fakeReturnPlugin = ['foo bar']
        result = self._pollerMuninModule.munin_list()
        self.assertEqual(result, ['foo', 'bar'])

    def test_muninModule_munin_fetch(self):
        # Init fake readline
        self._pollerMuninModule._s = self._fakeSocket._fakereadline

        # Send bad fetch
        self._fakeSocket._fakeReturnValue = ['foo']
        result = self._pollerMuninModule.munin_fetch("foo")
        self.assertEqual(result, {})
        # Send space fetch
        self._fakeSocket._fakeReturnValue = [' ','  ','.']
        result = self._pollerMuninModule.munin_fetch("foo")
        self.assertEqual(result, {})
        # Send good + space munin_fetch
        self._fakeSocket._fakeReturnValue = ['foo.value 10','  ','.']
        result = self._pollerMuninModule.munin_fetch("foo")
        self.assertEqual(result, {'foo': '10'})
        # Send good munin_fetch
        self._fakeSocket._fakeReturnValue = ['foo.value 152121','.']
        result = self._pollerMuninModule.munin_fetch("foo")
        self.assertEqual(result, {'foo' : '152121'})
        # Send good munin_fetch with comment
        self._fakeSocket._fakeReturnValue = ['# bar','foo.value 152121','.']
        result = self._pollerMuninModule.munin_fetch("foo")
        self.assertEqual(result, {'foo': '152121'} )

    def test_muninModule_munin_config(self):
        # Init fake readline
        self._pollerMuninModule._s = self._fakeSocket._fakereadline
        # Send bad config
        self._fakeSocket._fakeReturnConfig = ['foo']
        result = self._pollerMuninModule.munin_config("foo")
        self.assertEqual(result, {})
        # Send good empty munin_config
        self._fakeSocket._fakeReturnConfig = ['','.']
        result = self._pollerMuninModule.munin_config("foo")
        self.assertEqual(result, {})
        # Send good + comment munin_config
        self._fakeSocket._fakeReturnConfig = ['#bar','foo.draw line','graph_title bar','.']
        result = self._pollerMuninModule.munin_config("foo")
        self.assertEqual(result, {'foo': {'draw': 'line'}, 'graph_title': 'bar'})
        # Send good + comment + label with space
        self._fakeSocket._fakeReturnConfig = ['#bar','foo.label foolabel test','graph_title bar','.']
        result = self._pollerMuninModule.munin_config("foo")
        self.assertEqual(result, {'foo': {'label': 'foolabel test'}, 'graph_title': 'bar'})

    def test_muninModule_formatFetchData(self):
        # Init fake readline
        self._pollerMuninModule._s = self._fakeSocket._fakereadline
        # Send empty bad fetch
        self._fakeSocket._fakeReturnValue = ['']
        result = self._pollerMuninModule.formatFetchData("foo")
        self.assertEqual(result, None)
        # Send bad fetch (no value)
        self._fakeSocket._fakeReturnValue = ['foo','.']
        result = self._pollerMuninModule.formatFetchData("foo")
        self.assertEqual(result, None)
        # Send empty fetch
        self._fakeSocket._fakeReturnValue = ['.']
        result = self._pollerMuninModule.formatFetchData("foo")
        self.assertEqual(result, None)
        # Send good fetch
        self._fakeSocket._fakeReturnValue = ['foo.value 42','.']
        result = self._pollerMuninModule.formatFetchData("foo")
        self.assertEqual(result, {'TimeStamp': result['TimeStamp'], 'Values': {'foo': '42'}, 'Plugin': 'foo'})
        self.assertTrue(re.match('^[0-9]{10}$',result['TimeStamp']))
        # Test value return negative
        self._fakeSocket._fakeReturnValue = ['foo.value -42','.']
        result = self._pollerMuninModule.formatFetchData("foo")
        self.assertEqual(result['Values']['foo'], '-42')
        # Test value return negative float
        self._fakeSocket._fakeReturnValue = ['foo.value -4.2','.']
        result = self._pollerMuninModule.formatFetchData("foo")
        self.assertEqual(result['Values']['foo'], '-4.2')
        # Test value return Undefine
        self._fakeSocket._fakeReturnValue = ['foo.value U','.']
        result = self._pollerMuninModule.formatFetchData("foo")
        self.assertEqual(result['Values']['foo'], 'U')
        # Test value return bad value
        self._fakeSocket._fakeReturnValue = ['foo.value abc','.']
        result = self._pollerMuninModule.formatFetchData("foo")
        self.assertEqual(result['Values']['foo'], 'U')
        # Test value return one good + one bad value
        self._fakeSocket._fakeReturnValue = ['foo.value abc','bar.value 42','.']
        result = self._pollerMuninModule.formatFetchData("foo")
        self.assertEqual(result['Values'], {'foo': 'U', 'bar': '42'})


    def test_muninModule_formatFetchInfo(self):
        # Init fake readline
        self._pollerMuninModule._s = self._fakeSocket._fakereadline
        # Send empty bad fetch
        self._fakeSocket._fakeReturnConfig = ['']
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result, None)
        # Send empty fetch
        self._fakeSocket._fakeReturnConfig = ['.']
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result, None)
        # Send valid with 2 infos + no info for DS bar + base + graph describ
        self._fakeSocket._fakeReturnConfig = ['graph_info unit test','graph_args --base 1024','foo.min 0','foo.max 10','bar.bar gnu','.']
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result,
                {'Describ': 'unit test', 'Title': 'foo', 'Plugin': 'foo', 'Vlabel': '', 'Base': '1024', 'Infos':
                    {'foo': {'max': '10', 'id': 'foo', 'min': '0'},
                    'bar': {'bar': 'gnu','id': 'bar'}}
                , 'Order': ''})
        # Send valid with bad --base + title
        self._fakeSocket._fakeReturnConfig = ['graph_args --base fake','foo.min 0','.']
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result['Base'], '1000')
        # Send valid with title with space
        self._fakeSocket._fakeReturnConfig = ['graph_title foo bar','foo.min 0','.']
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result['Title'], 'foo bar')
         # Send valid with no DS
        self._fakeSocket._fakeReturnConfig = ['graph_title bar','.']
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result, None)
        # Send good fetch with no valid value
        self._fakeSocket._fakeReturnConfig = ['foo bar','.']
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result, None)
        # Plugin valid with no info on DS but have one value in fetch
        self._fakeSocket._fakeReturnValue = ['bar.value 3','.']
        self._fakeSocket._fakeReturnConfig = ['foo.min 0','.']
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result["Infos"], {'foo': {'id': 'foo', 'min': '0'}, 'bar': {'id': 'bar'}})
        # Plugin valid with no info but have 1 value in fetch
        self._fakeSocket._fakeReturnValue = ['bar.value 3','.']
        self._fakeSocket._fakeReturnConfig = ['graph_title foo','.']
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result["Infos"], {'bar': {'id': 'bar'}})
        # Send good fetch, test value regex on datasource
        self._fakeSocket._fakeReturnValue = ['bar.value 3','bar_.value 1','.']
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result["Infos"], {'bar': {'id': 'bar'}, 'bar_': {'id': 'bar_'}})

    def test_muninModule_getData(self):
        # Init fake readline
        self._pollerMuninModule._s = self._fakeSocket._fakereadline
        # Send good fetch
        self._fakeSocket._fakeReturnPlugin = ['foo']
        self._fakeSocket._fakeReturnValue  = ['foo.value 4.2','.']
        result = self._pollerMuninModule.getData()
        self.assertEqual(result, [{'TimeStamp': result[0]['TimeStamp'], 'Values': {'foo': '4.2'}, 'Plugin': 'foo'}])
        # Send plugin with no value
        self._fakeSocket._fakeReturnPlugin = ['foo']
        self._fakeSocket._fakeReturnValue  = ['.']
        result = self._pollerMuninModule.getData()
        self.assertEqual(result, [])
        # Test regex plugin match
        self._pollerMuninModule._plugins_enable="^foo_b.*$"
        self._fakeSocket._fakeReturnPlugin = ['foo']
        self._fakeSocket._fakeReturnValue  = ['foo.value 4.2','.']
        result = self._pollerMuninModule.getData()
        self.assertEqual(result, [])
        # Regex suite
        self._fakeSocket._fakeReturnPlugin = ['foo_bar']
        result = self._pollerMuninModule.getData()
        self.assertEqual(result[0]['Plugin'], 'foo_bar')
        # Reset regex
        self._pollerMuninModule._plugins_enable="^.*$"



    def test_muninModule_pluginsRefresh(self):
        # Init fake readline
        self._pollerMuninModule._s = self._fakeSocket._fakereadline
        # Send config with no DS
        self._fakeSocket._fakeReturnPlugin = ['foo']
        self._fakeSocket._fakeReturnValue  = ['.']
        result = self._pollerMuninModule.pluginsRefresh()
        self.assertEqual(result, [])
        # Send config with no DS
        self._fakeSocket._fakeReturnPlugin = ['foo']
        self._fakeSocket._fakeReturnConfig  = ['foo.min 0','.']
        result = self._pollerMuninModule.pluginsRefresh()
        self.assertEqual(result,
                [{'Describ': '', 'Title': 'foo', 'Plugin': 'foo', 'Vlabel': '', 'Base': '1000',
                    'Infos': {'foo': {'id': 'foo', 'min': '0'}}, 'Order': ''}
                ])
        # Test regex plugin match
        self._pollerMuninModule._plugins_enable="^foo_b.*$"
        self._fakeSocket._fakeReturnPlugin = ['foo']
        self._fakeSocket._fakeReturnConfig  = ['foo.min 0','.']
        result = self._pollerMuninModule.pluginsRefresh()
        self.assertEqual(result, [])
        # Regex suite
        self._fakeSocket._fakeReturnPlugin = ['foo_bar']
        result = self._pollerMuninModule.pluginsRefresh()
        self.assertEqual(result[0]['Plugin'], 'foo_bar')


