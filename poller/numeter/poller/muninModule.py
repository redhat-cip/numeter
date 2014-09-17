#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from modulesGeneric import ModulesGeneric
import re
import time
from logging import getLogger

import munin_connect


#
# Munin module
#
class MuninModule(ModulesGeneric):
    '''This poller module fetch configs and datas from a munin-node daemon.

       Configuration section for this module : ::

         [MuninModule]
         plugins_enable = ^.*$    ; Regexp matching plugins to fetch
         munin_host = 127.0.0.1   ; Munin Host
         munin_port = 4949        ; Munin Port
       '''

    def __init__(self, configParser=None):
        self._logger = getLogger(__name__)
        self._logger.info("Plugin Munin start")
        self._configParser = configParser
        self._munin_host = "127.0.0.1"
        self._munin_port = 4949
        self._plugins_enable = ".*"
        self.munin_connection = None
        self.watchdog = 1000 # watchdog for munin socket error

        if configParser: self.getParserConfig()
        self._logger.info("section MuninModule : plugins_enable = "
                        + self._plugins_enable)
        self._logger.info("section MuninModule : munin_host = "
                        + self._munin_host)
        self._logger.info("section MuninModule : munin_port = "
                        + str(self._munin_port))
        self.munin_connection = munin_connect.MuninConnection(self._munin_host,
                                                              self._munin_port)

    def getData(self):
        "get and return all data collected"

        # Get list of all plugins
        pluginList = self.munin_connection.munin_list()

        datas = []
        for plugin in pluginList:
            if re.match(self._plugins_enable, plugin):
                self._logger.info("MuninModule : get data for " + plugin)
                fetchResult = self.formatFetchData(plugin)
                if fetchResult == None: continue
                self._logger.debug("MuninModule : Value : " + str(fetchResult))
                datas.append(fetchResult)
        return datas


    def getInfo(self):
        "Return plugins info for refresh"

        pluginList = self.munin_connection.munin_list()

        infos = []
        for plugin in pluginList:
            if re.match(self._plugins_enable, plugin):
                self._logger.info("MuninModule : get Infos for " + plugin)
                fetchResult = self.formatFetchInfo(plugin)
                if fetchResult == None: continue
                self._logger.debug("MuninModule : infos : "
                            + str(fetchResult))
                infos.append(fetchResult)
        return infos



    def formatFetchData(self, plugin):
        "Execute fetch() and format data"
        # Fetch munin

        pluginData = self.munin_connection.munin_fetch(plugin)

        # If empty
        if pluginData == {}:
            return None

        # Get now timestamp
        nowTimestamp = "%s" % int(time.time())
        # Set plugin informations
        data = {  'TimeStamp': nowTimestamp,
                   'Plugin': plugin,
                   'Values': pluginData
        }
        return data


    def formatFetchInfo(self, plugin):

        "Execute config() and format infos"
        # Config munin
        pluginInfo = self.munin_connection.munin_config(plugin)

        # If empty
        if not pluginInfo:
            return None

        # Set plugin informations (defaul values)
        infos =  {    'Plugin': plugin,
                      'Base': '1000',
                      'Describ': '',
                      'Title': plugin,
                      'Vlabel': '',
                      'Order': '',
                      'Infos': {}
                 }

        # Set plugin info
        #valueInfos = {} #unused
        for key, value in pluginInfo.iteritems():
            if key == "graph_title":
                infos['Title'] = value
            elif key == 'graph_info':
                infos['Describ'] = value
            elif key == "graph_vlabel":
                infos['Vlabel'] = value
            elif key == "graph_order":
                infos['Order'] = value
            elif key == 'graph_category':
                infos['Category'] = value
            elif key == "graph_args":
                match = re.match("--base\s+([0-9]+)(\s+|$)", value)
                if match is not None:
                    infos['Base'] = match.group(1)
            # only values info has dict : '_run': {'warning': '92', 'label': '/run'}
            elif type(value) == type(dict()):
                value['id'] = key
                infos["Infos"][key] = value
            else: continue

        # Get DS with no infos
        fetchResult = self.formatFetchData(plugin)
        if fetchResult != None:
            # Concatenate
            tmp_ds = {}
            for key, value in fetchResult["Values"].iteritems():
                tmp_ds[key] = {'id': key}
            tmp_ds.update(infos["Infos"])
            infos["Infos"] = tmp_ds

        # If the munin plugin doesn't provide a graph order we define one
        if infos['Order'] == '':
            orderlist = []
            for key, value in pluginInfo.iteritems():
                if type(value) == type(dict()) and 'draw' in value:
                    if value['draw'] != 'STACK':
                        orderlist.insert(0, key)
                    else:
                        orderlist.append(key)
            infos['Order'] = ' '.join(orderlist)

        if infos["Infos"] == {}:
            return None
        else:
            return infos


    def getParserConfig(self):
        "Read configuration file"
        # plugins_enable
        if self._configParser.has_option('MuninModule', 'plugins_enable') \
        and self._configParser.get('MuninModule', 'plugins_enable'):
            self._plugins_enable = self._configParser.get('MuninModule'
                                        , 'plugins_enable')
        # munin_host
        if self._configParser.has_option('MuninModule', 'munin_host') \
        and self._configParser.get('MuninModule', 'munin_host'):
            self._munin_host = self._configParser.get('MuninModule'
                                        , 'munin_host')
        # munin_port
        if self._configParser.has_option('MuninModule', 'munin_port') \
        and self._configParser.getint('MuninModule', 'munin_port'):
            self._munin_port = self._configParser.getint('MuninModule'
                                        , 'munin_port')
