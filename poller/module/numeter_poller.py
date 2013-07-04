#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import time
import os
import json
from myRedisConnect import *
import socket
import re
import logging
import sys


import pprint # Debug (dumper)


#
# Poller
#
class myPoller:
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
        self._redis_password         = None
        self._redis_db               = 0
        self._redis_data_expire_time = 120
        self._redis_port             = 6379
        self._redis_host             = "127.0.0.1"
        self._plugin_number          = 0
        self.disable_pollerTimeToGo  = False

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

        if not self._simulate:
            # Open redis connexion
            self._redis_connexion = self.redisStartConnexion()
            # Clear old datas
            self.rediscleanDataExpired()

        # Lancement des modules + écriture des data dans redis
        self.loadModules()

        # End log time execution
        self._logger.warning("---- End : numeter_poller, "
            + str(self._plugin_number) + " Plugins in "
            + str(time.time() - self._startTime) + ", seconds.")


    def redisStartConnexion(self):
        "start redis connexion"
        redis_connexion = myRedisConnect(host=self._redis_host,
                                         port=self._redis_port,
                                         password=self._redis_password,
                                         db=self._redis_db)
        if redis_connexion._error:
            self._logger.critical("Redis connexion ERROR - Check server access or the password")
            exit(1)
        return redis_connexion


    def convertToJson(self, data):
        "Convert data to json"
        return json.dumps(data)



    def writeData(self, allDatas):
        "Write data in redis or file"
        if self._simulate:
            self._logger.info("Write data in file : " + self._simulate_file)
            self.writeInSimulateFile("===== Write DATAS =====")
            allDatasJson = self.convertToJson(allDatas)
            self.writeInSimulateFile(str(allDatasJson))
        else:
            self._logger.info("Write data in redis")
            allTimeStamps = []
            for data in allDatas:
                if data.has_key("TimeStamp") \
                and data.has_key("Plugin") \
                and re.match("[0-9]+",data["TimeStamp"]):
                    dataJson = self.convertToJson(data)
                    self._logger.info("Write TimeStamp " + data["TimeStamp"]
                                      + " -- plugin : "+data["Plugin"] )
                    self._logger.debug("Write TimeStamp " + data["TimeStamp"]
                                       + " -- plugin : " + data["Plugin"]
                                       + " -- value :"+str(dataJson))
                    self._redis_connexion.redis_zadd("DATAS",
                                                     dataJson,
                                                     int(data["TimeStamp"]))
                    allTimeStamps.append(data["TimeStamp"])
                    self._plugin_number = self._plugin_number + 1
            # Write all timeStamps
            seen = []
            for timeStamp in allTimeStamps:
                if timeStamp not in seen:
                    self._redis_connexion.redis_zadd("TimeStamp",
                                                     timeStamp,
                                                     int(timeStamp))
                    seen.append(timeStamp)




    def writeInfo(self, allInfos):
        "Write infos in redis or file"
        if self._simulate:
            self._logger.info("Write Infos in file : " + self._simulate_file)
            self.writeInSimulateFile("===== Write INFOS =====")
            allInfosJson = self.convertToJson(allInfos)
            self.writeInSimulateFile(str(allInfosJson))
            return []
        else:
            self._logger.info("Write Infos in redis")
            writedInfos = []
            for info in allInfos:
                if info.has_key("Plugin"):
                    infoJson = self.convertToJson(info)
                    self._logger.info("Write info -- plugin : "
                                      + info["Plugin"] )
                    self._logger.debug("Write info -- plugin : "
                                       + info["Plugin"]
                                       + " -- value :" + str(info))
                    self._redis_connexion.redis_hset("INFOS",
                                                     info["Plugin"],
                                                     infoJson)
                    writedInfos.append(info["Plugin"])
            return writedInfos



    def cleanInfo(self, writedInfos):
        "Clean infos in redis"

        # Get current plugin list
        currentPlugin = self._redis_connexion.redis_hkeys("INFOS")
        if currentPlugin == []:
            self._logger.info("Clean info -- nothing to do")
            return
        # Get the gap
        toDelete = list(set(currentPlugin) - set(writedInfos))
        # Same list do nothing
        if toDelete == []:
            self._logger.info("Clean info -- nothing to do : same Infos")
            return
        else: # Erase some plugin
            self._logger.info("Clean info -- clean plugins : " + str(toDelete))
            if self._simulate:
                self.writeInSimulateFile("===== Clean INFOS =====")
                self.writeInSimulateFile(str(toDelete))
            else:
                for plugin in toDelete:
                    self._redis_connexion.redis_hdel("INFOS", plugin)



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
            self._logger.info("Try to launch module : " + module)
            modImport = __import__(module)
            try:
                modClass = getattr(modImport, module)
                modObj = modClass(self._logger, self._configParse)
                # Get DATAS
                self._logger.info("Call plugin get data")
                allDatas = modObj.getData()
                self.writeData(allDatas)
                # Refresh config
                if self._need_refresh: 
                    self._logger.info("Call plugin info refresh")
                    # Get all infos
                    allInfos = modObj.pluginsRefresh()
                    # Write all infos
                    writedInfos.extend(self.writeInfo(allInfos))
                self._logger.info("Module : " + module + " Success")
                del(modObj)

            except (AttributeError, TypeError), e:
                self._logger.error("Module : " + module + " error :" + str(e))
                continue 
        # Exec fixe module
        # loadModules getMyInfo
        if self._need_refresh: 
            allInfos = []
            self._logger.info("Call plugin getMyInfo")
            allInfos = self.getMyInfo()
            self.writeInfo(allInfos)
            writedInfos.append('MyInfo')
            # Clean suppress plugins
            self.cleanInfo(writedInfos)



    def getMyInfo(self):
        "Read my infos in conf file"
        info = {}
        info["Plugin"]      = "MyInfo"
        info['Name']        = self._myInfo_name
        info['ID']          = self._myInfo_hostID
        info['Description'] = self._myInfo_description
#        info['Step']        = str(self._poller_time)
        infos = []
        infos.append(info) # Format info for self.writeInfo
        return infos



    def getgloballog(self):
        "Init logger (file and stdr)"
        # set file logger
        logger = logging.getLogger('numeter')
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
        nowTimestamp     = "%.0f" % time.time()
        # Si c'est le 1er lancement
        if not os.path.isfile(self._poller_time_file):
            self._logger.info("Poller pollerTimeToGo ok now")
            with open(self._poller_time_file, 'w') as lastTimeFile:
                lastTimeFile.write("%s %s" % (nowTimestamp, nowTimestamp))
            self._need_refresh = True
            return True
        else:
            with open(self._poller_time_file, 'rb') as lastTimeFile:
                lastTime     = lastTimeFile.read()
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
        # redis_host
        if self._configParse.has_option('global', 'redis_host') \
        and self._configParse.get('global', 'redis_host'):
            self._redis_host = self._configParse.get('global', 'redis_host')
            self._logger.info("Config : redis_host = " + self._redis_host)
        # redis_password
        if self._configParse.has_option('global', 'redis_password') \
        and self._configParse.get('global', 'redis_password'):
            self._redis_password = self._configParse.get('global', 'redis_password')
            self._logger.info("Config : redis_password = " + self._redis_password)
        # redis_port
        if self._configParse.has_option('global', 'redis_port') \
        and self._configParse.getint('global', 'redis_port'):
            self._redis_port = self._configParse.getint('global', 'redis_port')
            self._logger.info("Config : redis_port = " + str(self._redis_port))
        # redis_db
        if self._configParse.has_option('global', 'redis_db') \
        and self._configParse.getint('global', 'redis_db'):
            self._redis_db = self._configParse.getint('global', 'redis_db')
            self._logger.info("Config : redis_db = " + str(self._redis_db))
        # redis_data_expire_time
        if self._configParse.has_option('global', 'redis_data_expire_time') \
        and self._configParse.getint('global', 'redis_data_expire_time'):
            self._redis_data_expire_time = self._configParse.getint('global', 'redis_data_expire_time')
            self._logger.info("Config : redis_data_expire_time = " + str(self._redis_data_expire_time))
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


    def rediscleanDataExpired(self):
        "Suppression des data dans redis > à redis_data_expire_time"
        now              = time.strftime("%Y %m %d %H:%M", time.localtime())
        nowTimestamp     = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M')) # "%.0f" % supprime le .0 aprés le
        expireInSeconde  = self._redis_data_expire_time * 60
        dateMax          = str(int(nowTimestamp) - expireInSeconde)

        deleted = str(self._redis_connexion.redis_zremrangebyscore('DATAS', '-inf', dateMax))
        self._logger.info("Clear des data <= " + dateMax
                          + " Data deleted : " + deleted)
        
        deleted = str(self._redis_connexion.redis_zremrangebyscore('TimeStamp', '-inf', dateMax))
        self._logger.info("Clear des timestamp <= à " + dateMax
                          + " Data deleted : " + deleted)



