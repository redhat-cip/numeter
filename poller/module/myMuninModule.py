#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from modulesGeneric import ModulesGeneric
import re
import time
#import pprint  # Debug

#
# Munin module
#
class myMuninModule(ModulesGeneric):

    def __init__(self, logger, configParser=None):
        self._logger = logger
        self._logger.info("Plugin Munin start")
        self._configParser = configParser
        self._munin_host = "127.0.0.1"
        self._munin_port = 4949
        self._plugins_enable = ".*"
        self.munin_connection = None
        self.watchdog = 1000 # watchdog for munin socket error

        if configParser: self.getParserConfig()
        self._logger.info("section myMuninModule : plugins_enable = " 
                        + self._plugins_enable)
        self._logger.info("section myMuninModule : munin_host = " 
                        + self._munin_host)
        self._logger.info("section myMuninModule : munin_port = " 
                        + str(self._munin_port))


    def getData(self):
        "get and return all data collected"

        # Open new connect for each plugins because fucked plugin break the
        # read / write buffer
        #if self.munin_connection == None:
        #    # Start munin connexion
        #    self.munin_connect()

        # Get list of all plugins 
        pluginList = self.munin_list()

        datas = []
        for plugin in pluginList:
            if re.match(self._plugins_enable, plugin):  
                self._logger.info("myMuninModule : get data for " + plugin)
                fetchResult = self.formatFetchData(plugin)
                if fetchResult == None: continue
                self._logger.debug("myMuninModule : Value : " + str(fetchResult))
                datas.append(fetchResult)
        return datas


    def pluginsRefresh(self):
        "Return plugins info for refresh"

        #if self.munin_connection == None:
        #    # Start munin connexion
        #    self.munin_connect()

        pluginList = self.munin_list()

        infos = []
        for plugin in pluginList:
            if re.match(self._plugins_enable, plugin):  
                self._logger.info("myMuninModule : get Infos for " + plugin)
                fetchResult = self.formatFetchInfo(plugin)
                if fetchResult == None: continue
                self._logger.debug("myMuninModule : infos : " 
                            + str(fetchResult))
                infos.append(fetchResult)
        return infos



    def formatFetchData(self, plugin):
        "Execute fetch() and format data"
        # Fetch munin

        pluginData = self.munin_fetch(plugin)

        # If empty
        if pluginData == {}:
            return None

        # Get now timestamp
        now = time.strftime("%Y %m %d %H:%M", time.localtime())
        # Break this to allow poller under one min ?
        # "%.0f" % supprime le .0 aprés le timestamp
        nowTimestamp = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M'))
        # Set plugin informations
        data = {  'TimeStamp': nowTimestamp, 
                   'Plugin': plugin, 
                   'Values': pluginData
        }

        return data


    def formatFetchInfo(self, plugin):

        "Execute config() and format infos"
        # Config munin
        pluginInfo = self.munin_config(plugin)

        # If empty
        if pluginInfo == []:
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


    def munin_connect(self):
        self.munin_connection = socket.create_connection((self._munin_host
                                            , self._munin_port))
        self._s = self.munin_connection.makefile()
        self.hello_string = self._readline()

    def munin_close(self):
        self.munin_connection.close()


    def _readline(self):
        return self._s.readline().strip()


    def _iterline(self):
        watchdog = self.watchdog
        while watchdog > 0:
            watchdog = watchdog - 1
            line = self._readline()
            if not line:
                break
            elif line.startswith('#'):
                continue
            elif line == '.':
                break
            yield line


    def munin_fetch(self, key):
        # Start munin connexion
        self.munin_connect()
        self.munin_connection.sendall("fetch %s\n" % key)
        ret = {}
        for line in self._iterline():
            match = re.match("^([^\.]+)\.value", line)
            if match is None: continue
            key = match.group(1)
            match = re.match("^[^ ]+\s+([0-9\.U-]+)$", line)
            if match is not None: value = match.group(1)
            else: value = 'U'
            ret[key] = value
        # Close munin connexion to avoid fucked plugin
        self.munin_close()
        return ret


    def munin_list(self):
        # Get node name
        node = self.munin_nodes()
        # Start munin connexion
        self.munin_connect()
        self.munin_connection.sendall("list %s\n" % node)
        return_list = self._readline().split(' ')
        # Close munin connexion to avoid fucked plugin
        self.munin_close()
        return return_list if return_list != [''] else []


    def munin_nodes(self):
        # Start munin connexion
        self.munin_connect()
        self.munin_connection.sendall("nodes\n")
        return_node = [ line for line in self._iterline() ]
        # Close munin connexion to avoid fucked plugin
        self.munin_close()
        return return_node[0] if return_node else None


    def munin_config(self, key):
        # Start munin connexion
        self.munin_connect()
        self.munin_connection.sendall("config %s\n" % key)
        ret = {}
        for line in self._iterline():
            if line.startswith('graph_'):
                try:
                    key, value = line.split(' ', 1)
                    ret[key] = value
                except ValueError:
                    self._logger.info("myMuninModule : skipped key " + key) 
            else:
                # less sure but faster
                #key, rest = line.split('.', 1)
                #prop, value = rest.split(' ', 1)
                match = re.match("^([^\.]+)\.([^\ ]+)\s+(.+)", line)
                if match is None: continue
                key   = match.group(1)
                prop  = match.group(2)
                value = match.group(3)
                if not ret.get(key):
                    ret[key] = {}
                ret[key][prop] = value
        # Close munin connexion to avoid fucked plugin
        self.munin_close()
        return ret


    def getParserConfig(self):
        "Read configuration file"
        # plugins_enable
        if self._configParser.has_option('myMuninModule', 'plugins_enable') \
        and self._configParser.get('myMuninModule', 'plugins_enable'):
            self._plugins_enable = self._configParser.get('myMuninModule'
                                        , 'plugins_enable')
        # munin_host
        if self._configParser.has_option('myMuninModule', 'munin_host') \
        and self._configParser.get('myMuninModule', 'munin_host'):
            self._munin_host = self._configParser.get('myMuninModule'
                                        , 'munin_host')
        # munin_port
        if self._configParser.has_option('myMuninModule', 'munin_port') \
        and self._configParser.getint('myMuninModule', 'munin_port'):
            self._munin_port = self._configParser.getint('myMuninModule'
                                        , 'munin_port')

