#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import socket
import logging
import ConfigParser

myPath = os.path.abspath(os.path.dirname(__file__))

import  numeter.poller.munin_connect

import base as test_base

class fakereadline(object):
    def __init__(self):
        self.read_return = None
        self.count = -1
        return
    def set_return(self,lines):
        self.read_return = lines
        self.count = -1
    def __call__(self):
        return self.readline()
    def readline(self):
        if len(self.read_return) == 0:
            return
        elif self.count < len(self.read_return) - 1:
            self.count = self.count + 1
        return self.read_return[self.count]

class FakeMuninSock(numeter.poller.munin_connect.MuninSock):
    def __init__(self, host, port):
        pass
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        pass
    def close(self):
        pass
    def makefile(self):
        return self #._fakereadline
    def sendall(self,string):
        return self

class PollerMuninConnectTestCase(test_base.TestCase):

    def setUp(self):
        super(PollerMuninConnectTestCase, self).setUp()
        # Set logger None
        self._logger = logging.getLogger()
        fh = logging.FileHandler("/dev/null")
        fh.setLevel(logging.CRITICAL)
        self._logger.addHandler(fh)
        # Fake munin sock
        self._back_MuninSock = numeter.poller.munin_connect.MuninSock
        numeter.poller.munin_connect.MuninSock = FakeMuninSock
        # Start
        self._munin_connect = numeter.poller.munin_connect.MuninConnection(self._logger)
        # Fake readline
        self._fake_read = fakereadline()
        self._back_readline = self._munin_connect._readline
        self._munin_connect._readline = self._fake_read

    def tearDown(self):
        super(PollerMuninConnectTestCase, self).tearDown()
        self._munin_connect._readline = self._back_readline
        numeter.poller.munin_connect.MuninSock = self._back_MuninSock

    def test_muninModule_munin_nodes(self):
        # Send bad fetch default hostname
        self._fake_read.set_return(['foo'])
        result = self._munin_connect.munin_nodes()
        self.assertEqual(result, 'foo')
        # Send empty line
        self._fake_read.set_return(['','',''])
        result = self._munin_connect.munin_nodes()
        self.assertEqual(result, None)
        # Send good with all chars
        self._fake_read.set_return(['f.o-o_A9','.'])
        result = self._munin_connect.munin_nodes()
        self.assertEqual(result, 'f.o-o_A9')
        # Send good fetch with comment
        self._fake_read.set_return(['# bar','foo','.'])
        result = self._munin_connect.munin_nodes()
        self.assertEqual(result, 'foo')

    def test_muninModule_getList(self):
        # Send correct list
        self._fake_read.set_return(['plugin1 plugin2 plugin3'])
        result = self._munin_connect.munin_list()
        self.assertEqual(result, ['plugin1','plugin2', 'plugin3'])
        # Send list with one space
        self._fake_read.set_return([' foo bar'])
        result = self._munin_connect.munin_list()
        self.assertEqual(result, ['foo', 'bar'])
        # Send space list with \n
        self._fake_read.set_return([' '])
        result = self._munin_connect.munin_list()
        self.assertEqual(result, [])

    def test_muninModule_munin_fetch(self):
        # Send bad fetch
        self._fake_read.set_return(['bar'])
        result = self._munin_connect.munin_fetch('foo')
        self.assertEqual(result, {})
        # Send good and a space
        self._fake_read.set_return(['bar.value 10', '  '])
        result = self._munin_connect.munin_fetch('foo')
        self.assertEqual(result, {'bar': '10'})
        # Send 2 good values and one comment
        self._fake_read.set_return(['foo.value 152121', '# some dummy comment', 'bar.value -1.5'])
        result = self._munin_connect.munin_fetch('foo')
        self.assertEqual(result, {'bar': '-1.5', 'foo': '152121'})
        # Send good value and a error value remplaced by U
        self._fake_read.set_return(['foo.value 42', 'bar.value bla'])
        result = self._munin_connect.munin_fetch('foo')
        self.assertEqual(result, {'bar': 'U', 'foo': '42'})

    def test_muninModule_munin_config(self):
        # Send bad ignored key
        self._fake_read.set_return(['foo'])
        result = self._munin_connect.munin_config('foo')
        self.assertEqual(result, {})
        # Send good + comment munin_config
        self._fake_read.set_return(['#bar','foo.draw line','graph_title bar'])
        result = self._munin_connect.munin_config('foo')
        self.assertEqual(result, {'foo': {'draw': 'line'}, 'graph_title': 'bar'})
        # Send good + comment + label with space
        self._fake_read.set_return(['#bar', 'foo.label foolabel test', 'graph_title bar'])
        result = self._munin_connect.munin_config('foo')
        self.assertEqual(result, {'foo': {'label': 'foolabel test'}, 'graph_title': 'bar'})
