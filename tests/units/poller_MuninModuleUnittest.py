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

# Class fake socket
class myFakeMunin(object):
    fetch_return_value = None
    config_return_value = None
    list_return_value = None
    def __init__(self):
        pass
    def munin_fetch(self, plugin=None):
        return self.fetch_return_value
    def munin_config(self, plugin=None):
        return self.config_return_value
    def munin_list(self, plugin=None):
        return self.list_return_value

_logger = logging.getLogger()
fh = logging.FileHandler("/dev/null")
fh.setLevel(logging.CRITICAL)
_logger.addHandler(fh)

class PollerMuninModuleTestCase(test_base.TestCase):
#self.munin_connection = munin_connect.MuninConnection
# import munin_connect
    def setUp(self):
        super(PollerMuninModuleTestCase, self).setUp()
        # Set logger None
        self._logger = _logger
        # Set parser
        self._configParse = ConfigParser.RawConfigParser()
        self._configParse.read(myPath+"/poller_unittest.cfg")
        # Fake socker
        self._fakeMunin = myFakeMunin()
        # Start
        self._pollerMuninModule = myMuninModule(self._configParse)
        self._pollerMuninModule.munin_connection = self._fakeMunin
        # Make a shot name
        self._munin = self._pollerMuninModule.munin_connection
        self._pollerMuninModule._plugins_enable=".*"

    def tearDown(self):
        super(PollerMuninModuleTestCase, self).tearDown()

    def test_muninModule_formatFetchData(self):
        # Send empty bad fetch
        self._munin.fetch_return_value = {}
        result = self._pollerMuninModule.formatFetchData("foo")
        self.assertEqual(result, None)
        # Send good fetch
        self._munin.fetch_return_value = { 'bar':'42' }
        result = self._pollerMuninModule.formatFetchData("foo")
        self.assertEqual(result, {'TimeStamp': result['TimeStamp'], 'Values': {'bar': '42'}, 'Plugin': 'foo'})
        self.assertTrue(re.match('^[0-9]{10}$',result['TimeStamp']))

    def test_muninModule_formatFetchInfo(self):
        # Send empty config
        self._munin.config_return_value = {}
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result, None)
        # Send valid with 2 infos, no info for DS bar, base and graph describ
        #self._fakeMunin._fakeReturnConfig = ['graph_info unit test','graph_args --base 1024','foo.min 0','foo.max 10','bar.bar gnu','.']
        self._munin.config_return_value = {
                                            'graph_info':'unit test',
                                            'graph_title':'foo bar',
                                            'graph_vlabel':'',
                                            'graph_args':'--base 1024',
                                            'foo': {'max':'10', 'min':'0'},
                                            'bar': {'bar':'gnu'}
                                          }
        self._munin.fetch_return_value = {}
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result,
                {'Describ': 'unit test', 'Title': 'foo bar', 'Plugin': 'foo', 'Vlabel': '', 'Base': '1024', 'Infos':
                    {'foo': {'max': '10', 'id': 'foo', 'min': '0'},
                    'bar': {'bar': 'gnu','id': 'bar'}}
                , 'Order': ''})
        # Send valid with bad --base + title
        self._munin.config_return_value = {
                                            'graph_vlabel':'',
                                            'graph_args':'--base fake',
                                            'foo': {},
                                          }
        self._munin.fetch_return_value = {}
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result['Base'], '1000')
         # Send valid with no DS infos
        self._munin.config_return_value = {
                                            'graph_title':'foo',
                                          }
        self._munin.fetch_return_value = {}
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result, None)
        # Plugin valid with no info on DS but have one value in fetch
        self._munin.config_return_value = {
                                            'graph_title':'foo',
                                            'foo': {'min':'0'},
                                          }
        self._munin.fetch_return_value = {'bar':'3'}
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result["Infos"], {'foo': {'id': 'foo', 'min': '0'}, 'bar': {'id': 'bar'}})
        # Value declared as stack. Graph order must be genereted
        self._munin.config_return_value = {
                                            'graph_title':'foo',
                                            'foo': {'draw':'STACK'},
                                            'bar': {'draw':'LINE'},
                                          }
        self._munin.fetch_return_value = {}
        result = self._pollerMuninModule.formatFetchInfo("foo")
        self.assertEqual(result["Order"], "bar foo")

    def test_muninModule_getData(self):
        # Send good fetch
        self._munin.list_return_value = ['foo']
        self._munin.fetch_return_value = { 'bar':'4.2' }
        result = self._pollerMuninModule.getData()
        self.assertEqual(result, [{'TimeStamp': result[0]['TimeStamp'], 'Values': {'bar': '4.2'}, 'Plugin': 'foo'}])
        # Send plugin with no value
        self._munin.list_return_value = ['foo']
        self._munin.fetch_return_value = {}
        result = self._pollerMuninModule.getData()
        self.assertEqual(result, [])
        # Test regex plugin match
        self._pollerMuninModule._plugins_enable="^foo_b.*$"
        self._munin.list_return_value = ['foo']
        self._munin.fetch_return_value = { 'bar':'4.2' }
        result = self._pollerMuninModule.getData()
        self.assertEqual(result, [])
        # Matching regex
        self._pollerMuninModule._plugins_enable="^foo_b.*$"
        self._munin.list_return_value = ['foo_bar']
        self._munin.fetch_return_value = { 'bar':'4.2' }
        result = self._pollerMuninModule.getData()
        self.assertEqual(result[0]['Plugin'], 'foo_bar')
        # Reset regex
        self._pollerMuninModule._plugins_enable="^.*$"


    def test_muninModule_getInfo(self):
        # Send config with no DS
        self._munin.config_return_value = {'Title':'test'}
        self._munin.list_return_value = ['foo']
        self._munin.fetch_return_value = {}
        result = self._pollerMuninModule.getInfo()
        self.assertEqual(result, [])
        # Send config with no DS
        self._munin.list_return_value = ['foo']
        self._munin.fetch_return_value = {}
        self._munin.config_return_value = {
                                            'graph_title':'foo',
                                            'bar': {'min':'0'},
                                          }
        result = self._pollerMuninModule.getInfo()
        self.assertEqual(result,
                [{'Describ': '', 'Title': 'foo', 'Plugin': 'foo', 'Vlabel': '', 'Base': '1000',
                    'Infos': {'bar': {'id': 'bar', 'min': '0'}}, 'Order': ''}
                ])
        # Test regex plugin match
        self._pollerMuninModule._plugins_enable="^foo_b.*$"
        self._munin.config_return_value = {'graph_title':'foo'}
        self._munin.list_return_value = ['foo']
        self._munin.fetch_return_value = { 'bar':'4.2' }
        result = self._pollerMuninModule.getInfo()
        self.assertEqual(result, [])
        # Regex suite
        self._munin.list_return_value = ['foo_bar']
        self._munin.config_return_value = {'graph_title':'foo'}
        self._munin.fetch_return_value = { 'bar':'4.2' }
        result = self._pollerMuninModule.getInfo()
        self.assertEqual(result[0]['Plugin'], 'foo_bar')


