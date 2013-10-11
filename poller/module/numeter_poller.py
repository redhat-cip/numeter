#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import time
import os
import json
import socket
import re
import logging
import sys
from numeter.queue import client as NumeterQueueP
from cachelastvalue import CacheLastValue
from storeandforward import StoreAndForward

#
# Poller
#
class Poller(object):
    def __init__(self, configFile="/etc/numeter_poller.cfg"):

        self._startTime              = None
        self._poller_time_file       = "/var/run/numeter-poller"
        self._enable                 = False
        self._simulate               = False
        self._logLevel               = "debug"
        self._log_level_stdr         = "debug"
        self._log_path               = "/var/log/numeter.log"
        self._simulate_file          = "/tmp/numeter.simulate"
        self._poller_time            = 60
        self._plugins_refresh_time   = 300
        self._need_refresh           = False # Passe a True suivant le refresh_time
        self._rpc_hosts            = ['127.0.0.1:5672']
        self._plugin_number          = 0
        self.disable_pollerTimeToGo  = False
        self._cache = None

        # myInfo default value
        self._myInfo_name = socket.gethostname()
        self._myInfo_hostID = None
        self._myInfo_description = ""

        # Read de la conf
        self._configFile = configFile
        self.readConf()

    def startPoller(self):
        "Start the poller"

        self._startTime = time.time()
        self._plugin_number = 0

        # Poller enable ?
        if not self._enable:
            self._logger.warning("Poller disable, configuration enable = false")
            exit(2)
        # Test du dernier poller
        if not self.pollerTimeToGo():
            return False

        if not self._myInfo_hostID:
            self._logger.warning("Poller disable, configuration host_id = None")
            exit(2)

        # load cache for DERIVE and store and forward message
        with CacheLastValue(cache_file='/dev/shm/numeter_poller_cache.json',
                               logger='numeter') as self._cache, \
             StoreAndForward(cache_file='/dev/shm/numeter_poller_storeandforward.json',
                               logger='numeter') as self._store_and_forward:
            self.loadModules()

        # End log time execution
        self._logger.warning("---- End : numeter_poller, "
            + str(self._plugin_number) + " Plugins in "
            + str(time.time() - self._startTime) + ", seconds.")

    def convertToJson(self, data):
        "Convert data to json"
        return json.dumps(data)


    def _sendData(self, allDatas):
        "Send data in rpc"
        if self._simulate:
            self._logger.info("Write data in file : " + self._simulate_file)
            self.writeInSimulateFile("===== Write DATAS =====")
            allDatasJson = self.convertToJson(allDatas)
            self.writeInSimulateFile(str(allDatasJson))
        else:
            self._logger.info("Send data in rpc")
            allTimeStamps = []
            last_send_status = False
            for data in allDatas:
                if data.has_key("TimeStamp") \
                and data.has_key("Plugin") \
                and re.match("[0-9]+",data["TimeStamp"]):
                    for ds_name, ds_value in data['Values'].iteritems():
                        # Get gap if type is DERIVE, COUNTER, ...
                        key = '%s.%s' % (data["Plugin"], ds_name)
                        lastValue = self._cache.get_value(key)
                        if lastValue is not None:
                            if lastValue['value'] == 'U' \
                            or data['Values'][ds_name] == 'U':
                                gap = 'U'
                            else:
                                gap_value = float(data['Values'][ds_name]) - float(lastValue['value'])
                                timestamp_gap = int(data["TimeStamp"]) - int(lastValue['timestamp'])
                                gap = gap_value / timestamp_gap
                            # Update last value
                            self._cache.save_value( key=key,
                                    timestamp=data["TimeStamp"],
                                    value=data['Values'][ds_name])
                            # Replace value by gap for try
                            data['Values'][ds_name] = gap

                    dataJson = self.convertToJson(data)
                    self._logger.info("Send TimeStamp " + data["TimeStamp"]
                                      + " -- plugin : " + data["Plugin"] )
                    self._logger.debug("Send TimeStamp " + data["TimeStamp"]
                                       + " -- plugin : " + data["Plugin"]
                                       + " -- value :" + str(dataJson))

                    # send data in queue (if fail store)
                    last_send_status = self._store_and_forward_sendMsg(msgType='data',
                                                    plugin=data["Plugin"],
                                                    msgContent=dataJson)
                    allTimeStamps.append(data["TimeStamp"])
                    self._plugin_number = self._plugin_number + 1
            # Send stored datas
            if last_send_status:
                for msg in self._store_and_forward.consume():
                    if not self._store_and_forward_sendMsg(msgType=msg['msgType'],
                                 plugin=msg['plugin'],
                                 msgContent=msg['msgContent']):
                        break

    def _store_and_forward_sendMsg(self, msgType, plugin, msgContent):
        send_success = self._sendMsg(msgType, plugin, msgContent)
        if not send_success:
            self._store_and_forward.add_message(msgType,
                                                plugin,
                                                msgContent)
            self._logger.info("Adding message to store and forward file %s"
                                 % (plugin))
            return False
        return True


    def _sendMsg(self, msgType, plugin, msgContent):
        queue = NumeterQueueP.get_rpc_client(hosts=self._rpc_hosts)
        try:
            routing_key = '%s' % (self._myInfo_hostID)
            context = dict(topic=routing_key,
                           plugin=plugin,
                           type=msgType,
                           hostid=self._myInfo_hostID)
            args = {'message': msgContent}
            queue.poller_msg(context, topic=routing_key, args=args)
            return True
        except:
            self._logger.warning("Send message %s error : %s"
                                 % (routing_key, str(sys.exc_info())))
            return False


    def _sendInfo(self, allInfos):
        "Send info in rpc"
        if self._simulate:
            self._logger.info("Send Infos in file : " + self._simulate_file)
            self.writeInSimulateFile("===== SEND INFOS =====")
            allInfosJson = self.convertToJson(allInfos)
            self.writeInSimulateFile(str(allInfosJson))
            return []
        else:
            self._logger.info("Send info in rpc")
            writedInfos = []
            for info in allInfos:
                if info.has_key("Plugin"):
                    infoJson = self.convertToJson(info)
                    self._logger.info("Send info -- plugin : "
                                      + info["Plugin"] )
                    self._logger.debug("Send info -- plugin : "
                                       + info["Plugin"]
                                       + " -- value :" + str(info))
                    # send info in queue (if fail store)
                    last_send_status = self._sendMsg(msgType='info',
                                                    plugin=info["Plugin"],
                                                    msgContent=infoJson)
                    writedInfos.append(info["Plugin"])
                    # Say keep cache for DERIVE and other
                    # Do not try to cache MyInfo
                    if info["Plugin"] is 'MyInfo':
                        continue
                    # Check if ds need to be cached
                    # Send only if value is not in cache
                    for ds_name, ds_info in info.get("Infos", {}).iteritems():
                        key = '%s.%s' % (info["Plugin"], ds_name)
                        if 'type' in ds_info \
                        and self._cache.get_value(key) is None \
                        and ds_info['type'] in ('DERIVE', 'COUNTER', 'ABSOLUTE'):
                            self._cache.save_value(key=key,
                                             timestamp='000000000',
                                             value='U')
            return writedInfos


    def writeInSimulateFile(self, message):
        "Write in simulate file"
        logfile = open(self._simulate_file, 'a')
        logfile.write(message+"\n")
        logfile.close()



    def loadModules(self):
        "Get and write data / infos of all modules"
        # Load dynammic modules
        writedInfos = []
        for module in self._modules.split("|"):
            allDatas = allInfos = []
            self._logger.info("Try to launch module : %s" % module)
            try:
                (import_name, class_name) = module.split(':')
            except ValueError as e:
                self._logger.critical("Syntax error in module %s - %s" % (module,e))
                continue
            modImport = __import__(import_name, fromlist=[class_name])
            try:
                modClass = getattr(modImport, class_name)
                modObj = modClass(self._configParse)
                # Get DATAS
                self._logger.info("Call plugin get data")
                allDatas = modObj.getData()
                self._sendData(allDatas)
                # Refresh config
                if self._need_refresh:
                    self._logger.info("Call plugin info refresh")
                    # Get all infos
                    allInfos = modObj.getInfo()
                    # Write all infos
                    writedInfos.extend(self._sendInfo(allInfos))
                self._logger.info("Module : " + module + " Success")
                del(modObj)

            except (AttributeError, TypeError), e:
                self._logger.error("Module : %s error : %s" % (module, e))
                continue
            except Exception as e:
                self._logger.error("Module : %s Exception : %s" % (module, e))
                continue
        # Exec fixe module
        # loadModules getMyInfo
        if self._need_refresh:
            allInfos = []
            self._logger.info("Call plugin getMyInfo")
            allInfos = self.getMyInfo()
            self._sendInfo(allInfos)
            writedInfos.append('MyInfo')



    def getMyInfo(self):
        "Read my infos in conf file"
        info = {}
        info["Plugin"]      = "MyInfo"
        info['Name']        = self._myInfo_name
        info['ID']          = self._myInfo_hostID
        info['Description'] = self._myInfo_description
#        info['Step']        = str(self._poller_time)
        return [info]

    def getgloballog(self):
        "Init logger (file and stdr)"
        # set file logger
        logger = logging.getLogger()
        fh = logging.FileHandler(self._log_path)
        logger.addHandler(fh)
        if self._logLevel == "warning":
            logger.setLevel(logging.WARNING)
        elif self._logLevel == "error":
            logger.setLevel(logging.ERROR)
        elif self._logLevel == "info":
            logger.setLevel(logging.INFO)
        elif self._logLevel == "critical":
            logger.setLevel(logging.CRITICAL)
        else:
            logger.setLevel(logging.DEBUG)
        scriptname = sys.argv[0].split('/')[-1]
        formatter = logging.Formatter('%(asctime)s ('
                                      + scriptname
                                      + ') %(levelname)s -: %(message)s')
        fh.setFormatter(formatter)
        # set log to output error on stderr
        logsterr = logging.StreamHandler()
        logger.addHandler(logsterr)
        logsterr.setFormatter(logging.Formatter('%(levelname)s -: %(message)s'))
        if self._log_level_stdr == "warning":
            logsterr.setLevel(logging.WARNING)
        elif self._log_level_stdr == "info":
            logsterr.setLevel(logging.INFO)
        elif self._log_level_stdr == "error":
            logsterr.setLevel(logging.ERROR)
        elif self._log_level_stdr == "critical":
            logsterr.setLevel(logging.CRITICAL)
        else:
            logsterr.setLevel(logging.DEBUG)
        return logger


    def pollerTimeToGo(self):
        "LAST + poller_time <= NOW calcule aussi le refresh time"
        nowTimestamp = "%s" % int(time.time())

        # Si c'est le 1er lancement
        if not os.path.isfile(self._poller_time_file):
            self._logger.info("Poller pollerTimeToGo ok now")
            with open(self._poller_time_file, 'w') as lastTimeFile:
                lastTimeFile.write("%s %s" % (nowTimestamp, nowTimestamp))
            self._need_refresh = True
            return True
        else:
            with open(self._poller_time_file, 'rb') as lastTimeFile:
                lastTime = lastTimeFile.read()
            # If file is corrupt, reset
            if not re.match("^[0-9]{10} [0-9]{10}$", lastTime):
                lastTime = "0000000000 0000000000"
            # Si le temps est ok
            (lastPoller, lastRefresh) = lastTime.split(" ")
            # +10 temps de battement de cron offre 10 sec de souplesse
            if (int(lastPoller)+self._poller_time) <= (int(nowTimestamp)+10) \
            or self.disable_pollerTimeToGo:
                # Besoin d'un refresh ou non ?
                if (int(lastRefresh)+self._plugins_refresh_time) > int(nowTimestamp):
                    self._need_refresh = False
                    self._logger.info("Pas de refresh des informations plugins")
                else:
                    self._logger.info("Refresh des informations plugins")
                    lastRefresh = nowTimestamp
                    self._need_refresh = True

                with open(self._poller_time_file, 'w') as lastTimeFile:
                    lastTimeFile.write("%s %s" % (nowTimestamp, lastRefresh))
                self._logger.info("Poller pollerTimeToGo ok now")
                return True
            # Si c'est pas bon
            else:
                self._logger.warning("Poller to soon. pollerTimeToGo poller_time : "
                                     + str(self._poller_time)
                                     + " sec and refresh time : "
                                     + str(self._plugins_refresh_time)
                                     + " sec")
                self._need_refresh = False
                return False


    def readConf(self):
        "Read configuration file"
        self._configParse = ConfigParser.RawConfigParser()

        if self._configParse.read(self._configFile) == []: # If empty or not exist
            print ("CRIT - Read Config file "
                   + self._configFile
                   + " - ERROR (empty or doesn't exist)")
            exit(1)
        # GLOBAL
        # log_path
        if self._configParse.has_option('global', 'log_path') \
        and self._configParse.get('global', 'log_path'):
            self._log_path = self._configParse.get('global', 'log_path')
        # log_level
        if self._configParse.has_option('global', 'log_level') \
        and self._configParse.get('global', 'log_level'):
            self._logLevel = self._configParse.get('global', 'log_level')
        # log_level_stdr
        if self._configParse.has_option('global', 'log_level_stdr') \
        and self._configParse.get('global', 'log_level_stdr'):
            self._log_level_stdr = self._configParse.get('global', 'log_level_stdr')

        # Start logger
        self._logger = self.getgloballog()
        self._logger.info("----- Start Poller -----")

        # enable
        if self._configParse.has_option('global', 'enable') \
        and self._configParse.getboolean('global', 'enable'):
            self._enable = self._configParse.getboolean('global', 'enable')
            self._logger.info("Config : enable = " + str(self._enable))
        else:
            self._logger.info("Config : enable = " + str(self._enable))
        # simulate
        if self._configParse.has_option('global', 'simulate') \
        and self._configParse.getboolean('global', 'simulate'):
            self._simulate = self._configParse.getboolean('global', 'simulate')
            self._logger.info("Config : simulate = " + str(self._simulate))
        else:
            self._logger.info("Config : simulate = " + str(self._simulate))
        # simulate_file
        if self._configParse.has_option('global', 'simulate_file') \
        and self._configParse.get('global', 'simulate_file'):
            self._simulate_file = self._configParse.get('global', 'simulate_file')
            self._logger.info("Config : simulate_file = " + self._simulate_file)
        # modules
        if self._configParse.has_option('global', 'modules') \
        and self._configParse.get('global', 'modules'):
            self._modules = self._configParse.get('global', 'modules')
            self._logger.info("Config : modules = " + self._modules)
        # poller_time
        if self._configParse.has_option('global', 'poller_time') \
        and self._configParse.getint('global', 'poller_time'):
            self._poller_time = self._configParse.getint('global', 'poller_time')
            self._logger.info("Config : poller_time = " + str(self._poller_time))
        # poller_time_file
        if self._configParse.has_option('global', 'poller_time_file') \
        and self._configParse.get('global', 'poller_time_file'):
            self._poller_time_file = self._configParse.get('global', 'poller_time_file')
            self._logger.info("Config : poller_time_file = " + self._poller_time_file)
        # plugins_refresh_time
        if self._configParse.has_option('global', 'plugins_refresh_time') \
        and self._configParse.getint('global', 'plugins_refresh_time'):
            self._plugins_refresh_time = self._configParse.getint('global', 'plugins_refresh_time')
            self._logger.info("Config : plugins_refresh_time = " + str(self._plugins_refresh_time))
        # rpc_hosts
        if self._configParse.has_option('global', 'rpc_hosts') \
        and self._configParse.get('global', 'rpc_hosts'):
            self._rpc_hosts = self._configParse.get('global', 'rpc_hosts').split(',')
            self._logger.info("Config : rpc_hosts = " + ','.join(self._rpc_hosts))
        # getMyInfo - Name
        if self._configParse.has_option('MyInfo', 'name') \
        and self._configParse.get('MyInfo', 'name'):
            self._myInfo_name = self._configParse.get('MyInfo', 'name')
            self._logger.info("Config : myInfo_name = " + self._myInfo_name)
        # getMyInfo - hostID
        if self._configParse.has_option('MyInfo', 'host_id') \
        and self._configParse.get('MyInfo', 'host_id'):
            self._myInfo_hostID = self._configParse.get('MyInfo', 'host_id')
            self._logger.info("Config : myInfo_host_id = " + self._myInfo_hostID)
        # getMyInfo - Description
        if self._configParse.has_option('MyInfo', 'description') \
        and self._configParse.get('MyInfo', 'description'):
            self._myInfo_description = self._configParse.get('MyInfo', 'description')
            self._logger.info("Config : myInfo_description = " + self._myInfo_description)
