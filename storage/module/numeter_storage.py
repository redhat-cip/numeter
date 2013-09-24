#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import ConfigParser
import time
import os
import json
from myRedisConnect import myRedisConnect
from numeter_storage_endpoints import StorageEndpoint
from numeterQueue import server as NumeterQueueC
#import socket
import re
import logging
import sys
#import MySQLdb
import threading
import signal
import math
import hashlib
import random
import subprocess # Clean old wsp

#Python-whisper
import whisper


import pprint # Debug (dumper)

#
# myStorage
#
class myStorage:
    def __init__(self,configFile="/etc/numeter_storage.cfg"):

        # Default configuration
        self._startTime                 = time.time()
        self._enable                    = False
        self._simulate                  = False
        self._logLevel                  = "debug"
        self._log_level_stdr            = "debug"
        self._log_path                  = "/var/log/cron_numeter.log"
        self._simulate_file             = "/tmp/numeter.simulate"
        self._storage_thread            = 10
        self._max_hosts_by_thread       = 2
        self._max_data_by_hosts         = 20
        self._thread_wait_timeout       = 60
        self._rpc_hosts                 = ["127.0.0.1"]
        self._host_list_file            = "/dev/shm/numeter_storage_host_list"
        self._redis_storage_port        = 6379
        self._redis_storage_timeout     = 10
        self._redis_storage_password    = None
        self._redis_storage_host        = "127.0.0.1"
        self._redis_storage_db          = 0
        self._wsp_path                  = "/opt/numeter/wsp"
        self._wsp_path_md5_char         = 2
        self._wsp_clean_time            = 48 # 48h
        self._wsp_delete                = False
        self._redis_collector_port      = 6379
        self._redis_collector_timeout   = 10
        self._host_list                 = []
        self._host_listNumber           = 0
        self._hostNumber                = 0
        self._dataNumber                = 0
        self._pluginNumber              = 0
        self._sigint                    = False
        self._storage_name              = socket.gethostname()


        # Read de la conf
        self._configFile = configFile
        self.readConf()
        # Init other loggers
        self._init_others_logger(['oslo'])

    def startStorage(self):
        self._startTime = time.time()
        self._host_listNumber = 0
        self._hostNumber = 0
        self._dataNumber = 0
        self._pluginNumber = 0
        "Start storage"
        # storage enable ?
        if not self._enable:
            self._logger.warning("Numeter cron disable : "
                + "configuration enable = false")
            exit(2)

        if not self._simulate:
            # Open redis connexion
            self._logger.debug("Simulate=false : start redis connection")
            self._redis_connexion = self.redisStartConnexion()

            if self._redis_connexion._error:
                self._logger.critical("Redis storage connexion ERROR - "
                    + "Check redis access or password")
                exit(1)

        if not self._get_host_list():
            self._logger.critical("Numeter storage get host list fail")
            exit(1)

        # Time and thread param verification
        if not self.paramsVerification():
            self._logger.critical("Args verification error")
            exit(1)

        # start consumer
        self._queue_consumer = NumeterQueueC.get_rpc_server(topics=self._host_list,
                                                      server=self._storage_name,
                                                      endpoints=[StorageEndpoint(self)],
                                                      hosts=self._rpc_hosts)
        try:
            self._queue_consumer.start()
        except KeyboardInterrupt:
            self._queue_consumer.stop()
            #raise Exception('test catch')

        # End log time execution
        self._logger.warning("---- End : numeter_storage, "
            + str(self._host_listNumber) + " collector, "
            + str(self._hostNumber) + " Hosts, "
            + str(self._pluginNumber) + " Plugins, "
            + str(self._dataNumber) + " Datas in "
            + str(time.time()-self._startTime) + ", seconds.")



    def redisStartConnexion(self):
        # Open redis connexion
        redis_connection = myRedisConnect(host=self._redis_storage_host,
                                  port=self._redis_storage_port,
                                  socket_timeout=self._redis_storage_timeout,
                                  db=self._redis_storage_db,
                                  password=self._redis_storage_password)
        if redis_connection._error:
            self._logger.critical("Redis server connexion ERROR - "
                + "Check server access or the password")
            exit(1)
        return redis_connection

    def _init_others_logger(self,loggers=[]):
        "Set others logger in numeter log file"
        for name in loggers:
            # set file logger
            logger = logging.getLogger(name)
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
            formatter = logging.Formatter('%(asctime)s (' + scriptname
                            + ') %(levelname)s -: %(message)s')
            fh.setFormatter(formatter)

    def getgloballog(self):
        "Init du logger (fichier et stdr)"
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
        formatter = logging.Formatter('%(asctime)s (' + scriptname
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
  


    def readConf(self):
        "Read configuration file"
        self._configParse = ConfigParser.RawConfigParser()

        # If empty or not exist
        if self._configParse.read(self._configFile) == []:
            print ("CRIT - Read Config file " + self._configFile
                + "- ERROR (empty or doesn't exist)")
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
            self._log_level_stdr = self._configParse.get('global',
                                       'log_level_stdr')

        # Start logger
        self._logger = self.getgloballog()
        self._logger.info("----- Start Numeter Storage -----")

        # enable
        if self._configParse.has_option('global', 'enable') \
        and self._configParse.getboolean('global', 'enable'):
            self._enable = self._configParse.getboolean('global', 'enable')
            self._logger.info("Config : enable = "+str(self._enable))
        else:
            self._logger.info("Config : enable = "+str(self._enable))

        # simulate
        if self._configParse.has_option('global', 'simulate') \
        and self._configParse.getboolean('global', 'simulate'):
            self._simulate = self._configParse.getboolean('global', 'simulate')
            self._logger.info("Config : simulate = "+str(self._simulate))
        else:
            self._logger.info("Config : simulate = "+str(self._simulate))

        # simulate_file
        if self._configParse.has_option('global', 'simulate_file') \
        and self._configParse.get('global', 'simulate_file'):
            self._simulate_file = self._configParse.get('global', 'simulate_file')
            self._logger.info("Config : simulate_file = "+self._simulate_file)

        # storage_thread
        if self._configParse.has_option('global', 'storage_thread') \
        and self._configParse.getint('global', 'storage_thread'):
            self._storage_thread = self._configParse.getint('global',
                                       'storage_thread')
            self._logger.info("Config : storage_thread = "
                + str(self._storage_thread))
        # max_hosts_by_thread
        if self._configParse.has_option('global', 'max_hosts_by_thread') \
        and self._configParse.getint('global', 'max_hosts_by_thread'):
            self._max_hosts_by_thread = self._configParse.getint('global',
                                            'max_hosts_by_thread')
            self._logger.info("Config : max_hosts_by_thread = "
                + str(self._max_hosts_by_thread))
        # max_data_by_hosts
        if self._configParse.has_option('global', 'max_data_by_hosts') \
        and self._configParse.getint('global', 'max_data_by_hosts'):
            self._max_data_by_hosts = self._configParse.getint('global',
                                          'max_data_by_hosts')
            self._logger.info("Config : max_data_by_hosts = "
                + str(self._max_data_by_hosts))
        # thread_wait_timeout
        if self._configParse.has_option('global', 'thread_wait_timeout') \
        and self._configParse.getint('global', 'thread_wait_timeout'):
            self._thread_wait_timeout = self._configParse.getint('global',
                                            'thread_wait_timeout')
            self._logger.info("Config : thread_wait_timeout = "
                + str(self._thread_wait_timeout))

        # host_list_file
        if self._configParse.has_option('global', 'host_list_file') \
        and self._configParse.get('global', 'host_list_file'):
            self._host_list_file = self._configParse.get('global', 'host_list_file')
            self._logger.info("Config : host_list_file = "+self._host_list_file)

        # storage_name
        if self._configParse.has_option('global', 'storage_name') \
        and self._configParse.get('global', 'storage_name'):
            self._storage_name = self._configParse.get('global', 'storage_name')
            self._logger.info("Config : storage_name = "+self._storage_name)

        # rpc_hosts
        if self._configParse.has_option('global', 'rpc_hosts') \
        and self._configParse.get('global', 'rpc_hosts'):
            self._rpc_hosts = self._configParse.get('global', 'rpc_hosts').split(',')
            self._logger.info("Config : rpc_hosts = %s" % self._rpc_hosts)

        # redis_storage_port
        if self._configParse.has_option('global', 'redis_storage_port') \
        and self._configParse.getint('global', 'redis_storage_port'):
            self._redis_storage_port = self._configParse.getint('global', 'redis_storage_port')
            self._logger.info("Config : redis_storage_port = "+str(self._redis_storage_port))
        # redis_storage_timeout
        if self._configParse.has_option('global', 'redis_storage_timeout') \
        and self._configParse.getint('global', 'redis_storage_timeout'):
            self._redis_storage_timeout = self._configParse.getint('global', 'redis_storage_timeout')
            self._logger.info("Config : redis_storage_timeout = "+str(self._redis_storage_timeout))
        # redis_storage_password
        if self._configParse.has_option('global', 'redis_storage_password') \
        and self._configParse.get('global', 'redis_storage_password'):
            self._redis_storage_password = self._configParse.get('global', 'redis_storage_password')
            self._logger.info("Config : redis_storage_password = "+self._redis_storage_password)
        # redis_storage_host
        if self._configParse.has_option('global', 'redis_storage_host') \
        and self._configParse.get('global', 'redis_storage_host'):
            self._redis_storage_host = self._configParse.get('global', 'redis_storage_host')
            self._logger.info("Config : redis_storage_host = "+self._redis_storage_host)
        # redis_storage_db
        if self._configParse.has_option('global', 'redis_storage_db') \
        and self._configParse.getint('global', 'redis_storage_db'):
            self._redis_storage_db = self._configParse.getint('global', 'redis_storage_db')
            self._logger.info("Config : redis_storage_db = "+str(self._redis_storage_db))
        # wsp_path
        if self._configParse.has_option('global', 'wsp_path') \
        and self._configParse.get('global', 'wsp_path'):
            self._wsp_path = self._configParse.get('global', 'wsp_path')
            self._logger.info("Config : wsp_path = "+self._wsp_path)
        # wsp_path_md5_char
        if self._configParse.has_option('global', 'wsp_path_md5_char') \
        and self._configParse.getint('global', 'wsp_path_md5_char'):
            self._wsp_path_md5_char = self._configParse.getint('global', 'wsp_path_md5_char')
            self._logger.info("Config : wsp_path_md5_char = "+str(self._wsp_path_md5_char))
        # wsp_delete
        if self._configParse.has_option('global', 'wsp_delete') \
        and self._configParse.getboolean('global', 'wsp_delete'):
            self._wsp_delete = self._configParse.getboolean('global', 'wsp_delete')
            self._logger.info("Config : wsp_delete = "+str(self._wsp_delete))
        # wsp_clean_time
        if self._configParse.has_option('global', 'wsp_clean_time') \
        and self._configParse.getint('global', 'wsp_clean_time'):
            self._wsp_clean_time = self._configParse.getint('global', 'wsp_clean_time')
            self._logger.info("Config : wsp_clean_time = "+str(self._wsp_clean_time))

        # redis_collector_port
        if self._configParse.has_option('collector', 'redis_collector_port') \
        and self._configParse.getint('collector', 'redis_collector_port'):
            self._redis_collector_port = self._configParse.getint('collector', 'redis_collector_port')
            self._logger.info("Config : redis_collector_port = "+str(self._redis_collector_port))
        # redis_collector_timeout
        if self._configParse.has_option('collector', 'redis_collector_timeout') \
        and self._configParse.getint('collector', 'redis_collector_timeout'):
            self._redis_collector_timeout = self._configParse.getint('collector', 'redis_collector_timeout')
            self._logger.info("Config : redis_collector_timeout = "+str(self._redis_collector_timeout))



    def _get_host_list(self):
        "Get collector list"
        self._host_list = []
        try:
            # Open file
            host_file = open(self._host_list_file)
            # Parse result
            host_regex = r"^([^\s#]+)\s*$"
            regex = re.compile(host_regex)
            for line in host_file.readlines():
                result = regex.match(line)
                if result is not None:
                    self._host_list.append(result.group(1))
                    self._host_listNumber += 1
            # Close file
            host_file.close()
        except IOError, e:
            self._logger.critical("Open host_list file Error %s" % e)
            return False

        self._logger.info("Read file %s OK" % self._host_list_file)
        self._logger.info("Number of hosts : %s" % self._host_listNumber)
        return True



    def paramsVerification(self):
        "Args verification"
        if not self._storage_thread >= 1:
            self._logger.critical("paramsVerification Arg storage_thread : "
                + "Error (must be >=1)")
            return False
        if not self._max_hosts_by_thread >= 1:
            self._logger.critical("paramsVerification Arg "
                + "max_collector_by_thread : Error (must be >=1)")
            return False
        if not self._host_listNumber > 0:
            self._logger.critical("paramsVerification Arg "
                + "collectorListNumber : Error (must be >0)")
            return False
        self._logger.debug("Threads paramsVerification : OK")
        return True



    def sighandler(self, num, frame):
        "Start threads"
        self._sigint = True
        self._logger.warning("Thread Get sighandler !")


    def jsonToPython(self,data):
        "Convert json to python"
        try:
            pythonData = json.loads(data)
        except:
            pythonData = {}
        return pythonData


    def pythonToJson(self,data):
        "Convert python to json"
        try:
            jsonData = json.dumps(data)
        except:
            jsonData = {}
        return jsonData


    def _write_data(self, hostID, plugin, data_json):

        # For each plugin
        if plugin == None:
            return False

        data =  self.jsonToPython(data_json)
        data_timestamp = data.get('TimeStamp')

        # TODO dont write data if no infos

        # Get data_path
        data_path = self._redis_connexion.redis_hget("WSP_PATH", hostID)
        if data_path is None:
            return False

        wspPath = '%s/%s' % (data_path, plugin)
        for ds_name, value in data["Values"].iteritems():

            ds_path = '%s/%s.wsp' % (wspPath, ds_name)
            # Create wsp file - config wsp here
            if not os.path.isfile(ds_path):
                self._logger.warning("writewsp host : %s Create wsp file : %s"
                                        % (hostID, ds_path))
                # Create directory
                if not os.path.exists(wspPath):
                    try:
                        os.makedirs(wspPath)
                        self._logger.info("writewsp host : %s make directory : %s"
                                            % (hostID, wspPath))
                    except OSError:
                        self._logger.error("writewsp host : %s can't make directory : %s"
                                            % (hostID, wspPath))
                        continue
                try:
                    whisper.create(ds_path, 
                                   [(60, 1440),   # --- Daily (1 Minute Average)
                                   (300, 2016),   # --- Weekly (5 Minute Average)
                                   (600, 4608),   # --- Monthly (10 Min Average)
                                   (3600, 8784)]) # --- Yearly (1 Hour Average)
                except Exception as e:
                    self._logger.error("writewsp host : %s Create wsp Error %s"
                        % (hostID, str(e)))
                    continue
            # Update whisper
            try:
                self._logger.debug("writewsp host : %s Update wsp "
                                   "Timestamp %s For value %s in file %s" 
                                    % (hostID, data_timestamp, value, ds_path))
                whisper.update(ds_path, str(value), str(data_timestamp) )
            except Exception as e:
                self._logger.error("writewsp host : %s Update Error %s - %s"
                                    % (hostID, ds_path, e))
                continue
        return True
        

    def writewsp(self, sortedTS, hostAllDatas, host, basewspPath):
        "Write wsp with python-whisper"

        # For each plugin
        for plugin in hostAllDatas["Infos"]:
            if plugin == "MyInfo":
                continue

            # For each DS
            if not hostAllDatas["Infos"][plugin].has_key("Infos"):
                self._logger.error("writewsp host : " + host 
                    + " Plugin : " + plugin
                    + " don't have Infos, can't write data")
                continue
            for DSname in hostAllDatas["Infos"][plugin]["Infos"]:
                DSname = str(DSname)

                # Create wsp file - config wsp here
                wspPath = str(basewspPath+"/"+plugin)

                if not os.path.isfile(wspPath+"/"+DSname+".wsp"):
                    self._logger.warning("writewsp host : " + host 
                        + " Create wsp file : "+wspPath+"/"+DSname+".wsp")
                    # Create directory
                    if not os.path.exists(wspPath):
                        try:
                            os.makedirs(wspPath)
                            self._logger.info("writewsp host : " + host \
                            + " make directory :" + wspPath)
                        except OSError:
                            self._logger.error("writewsp host : " + host \
                            + " can't make directory :" + wspPath)
                            continue
                    try:
                        whisper.create(wspPath+"/"+DSname+".wsp",[(60, 1440),(300, 2016),(600, 4608),(3600, 8784)])
                    except Exception as e:
                        self._logger.error("writewsp host : " + host
                            + " Create wsp Error "
                            + str(e))
                        continue

                ## For each TS
                for TS in sortedTS:
                    try:
                        self._logger.error("writewsp host : " + host
                                + " Update wsp DEBUG Timestamp "
                                + str(TS) 
                                + " For value "
                                + str(hostAllDatas["Datas"][plugin][TS][DSname])
                                + " in file "
                                + str(wspPath+"/"+DSname+".wsp"))
                        whisper.update(wspPath+"/"+DSname+".wsp", 
                            str(hostAllDatas["Datas"][plugin][TS][DSname]), str(TS) )
                    except Exception as e:
                        self._logger.error("writewsp host : " + host
                            + " Update Error "
                            + str(e))
                        continue
        return True

    def _get_hostIDHash(self, hostID):
        "Get cached hostID hash or add in cache"
        hostIDHash = self._redis_connexion.redis_hget("HOST_ID",hostID)
        if hostIDHash == None:
            hostIDHash = hashlib.md5()
            hostIDHash.update(hostID)
            # Get X first char in md5 sum X=_wsp_path_md5_char 
            hostIDHash = hostIDHash.hexdigest()[0:self._wsp_path_md5_char]
            # Update redis cache
            self._redis_connexion.redis_hset("HOST_ID",hostID,hostIDHash)
            # Log
            self._logger.debug("_get_hostIDHash : %s Set new md5(%s)"
                               % (hostIDHash, hostID))
        return hostIDHash

    def _write_info(self, hostID, info_json):
        # info=   {    'Plugin': plugin, 
        #               'Base': '1000', 
        #               'ClientHash': 'md5(client)', <---- add by this function (in MyInfo)
        #               'Describ': '', 
        #               'Title': plugin, 
        #               'Vlabel': '', 
        #               'Order': '', 
        #               'Infos': {
        #                    "down" : {"type": "COUNTER", "id": "down", "label": "received"},
        #                     "up" : {"type": "COUNTER", "id": "up", "label": "upload"},
        #                }
        #          }
        info =  self.jsonToPython(info_json)
        plugin = info.get('Plugin', None)

        self._logger.debug("_write_infos  hostID : %s -- plugin : %s" 
                                % (hostID, plugin))

        # Get infos
        if info == {} \
        or ( plugin != "MyInfo" \
        and ( not info.has_key("Infos") or info["Infos"] == {} )):
            self._logger.warning("_write_infos  hostID : error, no Infos %s -- plugin : %s" 
                                    % (hostID, plugin))
            return False

        if plugin == "MyInfo":
            # Add hash + filtered and other (see in comments)
            if not "ID" in info or not "Name" in info:
                self._logger.error("_write_infos  hostID : error, no Infos %s -- plugin : %s" 
                                    % (hostID, plugin))
                return False
            # Get hash from cache for data path
            hostIDHash = self._get_hostIDHash(hostID)
            HostIDFiltredName = re.sub("[ \"/.']","",hostID)
            info['hostIDHash'] = hostIDHash
            info['HostIDFiltredName'] = HostIDFiltredName
            info_json = self.pythonToJson(info)
            self._redis_connexion.redis_hset("HOSTS", hostID, info_json)

            # Write client infos in redis
            wspPath = str('%s/%s/%s' % (self._wsp_path, hostIDHash, HostIDFiltredName))
            self._redis_connexion.redis_hset("WSP_PATH", hostID, wspPath)
        else:
            self._redis_connexion.redis_hset("INFOS@%s" % hostID, plugin, info_json)
        return True


    def getInfos(self,redisCollector,host):
        "get and write hosts infos from collector"

        # Init
        hostInfos={}
        # Writed Infos 
        writedInfos = []
        wspPath     = None
        # Get plugin INFOS@host
        allInfos = redisCollector.redis_hgetall("INFOS@"+host)

        self._pluginNumber = self._pluginNumber + len(allInfos)
        
        # is empty ?
        if allInfos == {}:
            self._logger.info("getInfos host : " + host 
                            + "INFOS@"+host+" empty")
            return [],{},None

        # infos=   {    'Plugin': plugin, 
        #               'Base': '1000', 
        #               'ClientHash': 'md5(client)', <---- add by this function (in MyInfo)
        #               'Describ': '', 
        #               'Title': plugin, 
        #               'Vlabel': '', 
        #               'Order': '', 
        #               'Infos': {
        #                    "down" : {"type": "COUNTER", "id": "down", "label": "received"},
        #                     "up" : {"type": "COUNTER", "id": "up", "label": "upload"},
        #                }
        #          }

        # --- Read all infos
        # For each plugin 
        for plugin,infoJson in allInfos.iteritems():

            # Log
            self._logger.debug("getInfos host : " + host 
                            + "Get plugin : "+plugin)

            # Get infos
            info = self.jsonToPython(infoJson)
            if info == {} \
            or ( plugin != "MyInfo" \
            and ( not info.has_key("Infos") or info["Infos"] == {} )):
                continue

            hostInfos[plugin]={}
            hostInfos[plugin]=info

            if plugin != "MyInfo":
                # Write infos in redis
                self._redis_connexion.redis_hset("INFOS@"+host, plugin, infoJson)
                writedInfos.append(plugin)

        # If no MyInfo, exit
        if not hostInfos.has_key("MyInfo") \
        or not hostInfos['MyInfo'].has_key("ID") \
        or not hostInfos['MyInfo'].has_key("Name"):
            self._logger.error("getInfos host : " + host
                + " No plugin MyInfo or bad entry : Host ignored")
            return [],{},None

        # Add HostIDMD5 to hostinfo (Used in wsppath)
        hostID = hostInfos["MyInfo"]["ID"]
        hostIDHash = self._redis_connexion.redis_hget("HOST_ID",hostID)

        # Get md5sum cache
        if hostIDHash == None:
            hostIDHash = ""
            hostIDHash = hashlib.md5()
            hostIDHash.update(hostID)
            # Get X first char in md5 sum X=_wsp_path_md5_char 
            hostIDHash = hostIDHash.hexdigest()[0:self._wsp_path_md5_char]
            # Update redis CLIENTS
            self._redis_connexion.redis_hset("HOST_ID",hostID,hostIDHash)
            # Log
            self._logger.debug("getInfos host : " + host 
                            + "Set new md5("+hostID+") : "+hostIDHash)
        else :
            # Log
            self._logger.debug("getInfos host : " + host 
                            + "Get md5("+hostID+") : "+hostIDHash+" from redis")

        hostInfos["MyInfo"]["HostIDHash"]        = hostIDHash
        hostInfos["MyInfo"]["HostIDFiltredName"] = re.sub("[ \"/.']","",hostID)

        # Write client infos in redis
        wspPath = str(self._wsp_path + "/" + hostIDHash + "/"
                      + hostInfos["MyInfo"]["HostIDFiltredName"])

        self._redis_connexion.redis_hset("WSP_PATH", hostID, wspPath)
        self._redis_connexion.redis_hset("HOSTS", hostID,
                                         self.pythonToJson(hostInfos["MyInfo"]))
        # MyInfo is not write in redis INFOS@... but it is use by writeWSP* so writedInfos.append
        writedInfos.append("MyInfo")
        #self._redis_connexion.redis_hset("INFOS@"+host, "MyInfo", self.pythonToJson(hostInfos["MyInfo"]))

        return writedInfos, hostInfos, wspPath





    def getData(self,redisCollector,host):
        "get and write hosts Data from collector"

        # Init
        hostDatas={}

        # Get plugin INFOS@host
        allTS = redisCollector.redis_zrangebyscore("TS@"+host, "-inf", "+inf",
                                                   start=0,
                                                   num=self._max_data_by_hosts)

        # is empty ?
        if allTS == {} or allTS == []:
            self._logger.info("getData host : " + host 
                            + "TS@"+host+" empty")
            return [], {}

        # Sort TS for rrd update
        allTS.sort()

        # Fetch datas
        allhostDatasJson = redisCollector.redis_zrangebyscore("DATAS@" + host,
                                                              allTS[0],
                                                              allTS[-1])
        if allhostDatasJson == []: # If TS have no data, clear this TS
            redisCollector.redis_zremrangebyscore("TS@"+host,allTS[0],allTS[-1])
            return [], {}

        self._dataNumber = self._dataNumber + len(allhostDatasJson)
        for dataJson in allhostDatasJson:
            data = self.jsonToPython(dataJson)

            # If bad data nexte
            if not data.has_key("Plugin") or not data.has_key("TimeStamp"):
                continue

            if not data["Plugin"] in hostDatas:
                hostDatas[data["Plugin"]]={}

            hostDatas[data["Plugin"]][data['TimeStamp']] = data['Values']

        # Clear old buggy datas (if data are older than last TS, delete them)
        redisCollector.redis_zremrangebyscore("DATAS@"+host,'-inf','('+allTS[0])

        return allTS, hostDatas




    def getHostList(self,collectorLine):
        "get and write hosts Data from collector"

        # Init
        hostList=[]

        # Get password and db
        collector        = collectorLine['host']
        redis_pass  = None
        redis_db    = "0"
        if collectorLine.has_key('db'):
            redis_db = collectorLine['db']
        if collectorLine.has_key('password'):
            redis_pass = collectorLine['password']

        # Get redis connexion collector
        redisCollector = myRedisConnect(host=collector,
                                  port=self._redis_collector_port,
                                  socket_timeout=self._redis_collector_timeout,
                                  db=redis_db,
                                  password=redis_pass)
        # If error goto next
        if redisCollector._error:
            self._logger.error("getHostList for " + collector 
                             + " redis connexion ERROR " + collector)
            return []
        else :
            self._logger.info("getHostList for " + collector
                             + " redis connexion OK " + collector)

        # Get HOSTS list
        hostList = redisCollector.redis_hvals("HOSTS")

        return hostList



    def cleanInfo(self,writedInfos,hostID):
        "Clean info in redis and wsp"
        # Get current plugin list
        currentPlugin = self._redis_connexion.redis_hkeys("INFOS@"+hostID)
        if currentPlugin == []:
            self._logger.info("Redis - Clean info -- nothing to do" )
            return
        # Get the gap
        toDelete=list(set(currentPlugin)-set(writedInfos))

        # Clean notify
        if not self._wsp_delete: 
            # Clean reappeared plugin 
            for plugin in writedInfos:
                self._redis_connexion.redis_hdel("DELETED_PLUGINS",hostID
                                                 + "@" + plugin)

        # Same list do nothing
        if toDelete == []:
            self._logger.info("Redis - Clean info -- nothing to delete" )
            return
        else: # Erase some plugin
            self._logger.info("Redis - Clean info -- clean plugins : "
                + str(toDelete) )
            wspPath = self._redis_connexion.redis_hget("WSP_PATH",hostID)
            if wspPath == None:
                self._logger.error("Redis - Clean info -- "
                    + "Can't get wsp path for " + hostID + " stop")
                return
            if self._wsp_delete: # Erase wsp
                for plugin in toDelete:
                    self._logger.warning("Redis - Clean info -- delete "
                        + wspPath + "/"+plugin)
                    # Delete plugin Infos
                    self._redis_connexion.redis_hdel("INFOS@"+hostID,plugin)
                    # Delete wsp
                    os.system("rm -Rf "+wspPath+"/"+plugin)
            else: # Notify in redis
                for plugin in toDelete:
                    self._logger.info("Redis - Clean info -- "
                        + "notify DELETED_PLUGINS " + plugin )
                    # Delete plugin Infos
                    self._redis_connexion.redis_hdel("INFOS@"+hostID,plugin)
                    # Set notify
                    self._redis_connexion.redis_hset("DELETED_PLUGINS",hostID
                        + "@" + plugin, wspPath + "/" + plugin)



    def cleanHosts(self,writedHosts):
        "Clean info in redis and wsp"
        # Get hostListe
        currentHosts = []

        # Get current hosts list
        currentHosts = self._redis_connexion.redis_hkeys("HOSTS")

        if currentHosts == []:
            self._logger.info("Clean hosts -- nothing to do" )
            return
        # Get the gap
        toDelete=list(set(currentHosts)-set(writedHosts))

        # Clean notify
        if not self._wsp_delete: 
            # Clean reappeared hosts 
            for hostID in writedHosts:
                self._redis_connexion.redis_hdel("DELETED_HOSTS",hostID)

        # Same list do nothing
        if toDelete == []:
            self._logger.info("Clean Hosts -- nothing to do : same Hosts" )
            return
        else: # Erase some hosts
            self._logger.warning("Redis - Clean hosts -- clean hosts : "
                + str(toDelete) )

            for hostID in toDelete:
                wspPath = self._redis_connexion.redis_hget("WSP_PATH",hostID)
                if wspPath == None:
                    self._logger.error("Redis - Clean hosts -- "
                        + "Can't get wsp path for " + hostID + " stop")
                    continue

                if self._wsp_delete: # Erase wsp
                    self._logger.warning("Redis - Clean hosts -- delete wsp "
                        + wspPath)
                    # Delete wsp
                    os.system("rm -Rf "+wspPath)
                else: # Notify in redis
                    self._logger.info("Redis - Clean hosts -- "
                        + "notify DELETED_HOSTS " + hostID )
                    # Set notify
                    self._redis_connexion.redis_hset("DELETED_HOSTS", hostID,
                                                     wspPath)

                # Delete related infos
                self._redis_connexion.redis_hdel("HOSTS",hostID)
                self._redis_connexion.redis_hdel("HOST_ID",hostID)
                self._redis_connexion.redis_hdel("WSP_PATH",hostID)
                # Delete infos
                for plugin in self._redis_connexion.redis_hkeys("INFOS@"
                                                                + hostID):
                     self._redis_connexion.redis_hdel("INFOS@" + hostID, plugin)


    def cleanOldWSP(self):
        "Clean old wsps"

        # Get last clean time
        lastFetch = self._redis_connexion.redis_get("LAST_WSP_CLEAN")
        now = time.strftime("%Y %m %d %H", time.localtime())
        # "%.0f" % supprime le .0 aprés le timestamp
        nowTimestamp = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H'))

        if lastFetch == None  \
        or (int(lastFetch)+(self._wsp_clean_time*60*60)) <= int(nowTimestamp) \
        or not re.match("^[0-9]{10}$",lastFetch):
            wspDelete = []

            # Set the new time
            self._redis_connexion.redis_set("LAST_WSP_CLEAN",nowTimestamp)

            if not os.path.isdir(self._wsp_path):
                self._logger.warning("Clean old WSP -- path wsp "
                    + self._wsp_path + " not found")
                return []

            if self._wsp_delete: # Erase wsp

                # Delete wsp
                process = subprocess.Popen("find " + self._wsp_path 
                + " -mmin +" + str(self._wsp_clean_time*60) 
                + " -type f" 
                + " -print" 
                + " -delete" , shell=True, stdout=subprocess.PIPE)
                (result, stderr) =  process.communicate()
                self._logger.warning("Clean old WSP -- delete wsp : "
                    + str(result))
                wspDelete = result.split()

                # Clean empty dirs
                process = subprocess.Popen("find " + self._wsp_path 
                + " -type d"
                + " -empty" 
                + " -print"
                + " -delete" , shell=True, stdout=subprocess.PIPE)
                (result, stderr) =  process.communicate()
                self._logger.warning("Clean old WSP -- delete empty dirs : "
                    + str(result))
                return wspDelete

            else : # Just notify
                process = subprocess.Popen("find " + self._wsp_path
                    + " -mmin +" + str(self._wsp_clean_time*60)
                    + " -type f", shell=True, stdout=subprocess.PIPE)
                (result, stderr) =  process.communicate()
                self._logger.info("Clean old WSP -- notify OLD_WSP : "
                    + str(lastFetch))
                wspDelete = result.split()
                self._redis_connexion.redis_set("OLD_WSP",
                                                self.pythonToJson(wspDelete))
                return wspDelete

        else :
            self._logger.info("Clean old WSP -- not this time. Last clean : "
                + str(lastFetch))
            return []




    def worker(self,threadId, sema,collectorLine,hostsList=[],simulateFileOpen=None):
        "Thread"
        #time.sleep(0)  # Debug add time
        simulateBuffer=[]
        
        self._logger.debug("Thread worker " + str(threadId) 
                          + " with collector : " + str(collectorLine))

        # Get password and db
        collector        = collectorLine['host']
        redis_pass = collectorLine['password'] \
            if collectorLine.has_key('password') else None
        redis_db = collectorLine['db'] \
            if collectorLine.has_key('db') else "0"

        # Get redis connexion collector
        redisCollector = myRedisConnect(host=collector,
                                   port=self._redis_collector_port,
                                   socket_timeout=self._redis_collector_timeout,
                                   db=redis_db,
                                   password=redis_pass)
        # If error goto next
        if redisCollector._error:
            self._logger.error("Worker " + str(threadId) 
                             + " redis connexion ERROR for collector : "
                             + collector)
            return False
        else :
            self._logger.info("Worker " + str(threadId) 
                             + " redis connexion OK for collector : " 
                             + collector)

        # For stats
        self._hostNumber = self._hostNumber + len(hostsList)

        # Pour chaque hosts
        for hostID in hostsList:

            # Reset data tabs
            hostAllDatas = {}

            # Get Infos
            (writedInfo, hostAllDatas["Infos"], hostWSPPath) = self.getInfos(redisCollector,hostID)
            self._logger.info( "Worker " + str(threadId) + " host : " + hostID
                + " getInfos")
            if hostAllDatas["Infos"] == {}:
                self._logger.info( "Worker " + str(threadId) + " host : "
                    + hostID + " getInfos empty")
                continue
            else:
                # Clean Infos (delete only plugins)
                self.cleanInfo(writedInfo,hostID)

            # Get Data
            (sortedTS, hostAllDatas["Datas"]) = self.getData(redisCollector,
                                                             hostID)
            self._logger.info( "Worker " + str(threadId) + " host : "
                + hostID + " getDatas")
            if hostAllDatas["Datas"] == {}:
                self._logger.info( "Worker " + str(threadId) + " host : "
                    + hostID + " getData empty")
                continue
            else:
                # Write wsp 
                self._logger.info( "Worker " + str(threadId) + " host : "
                    + hostID + " writewsp")
                self.writewsp(sortedTS, hostAllDatas,
                                  hostID, hostWSPPath)
                # Clear data 
                redisCollector.redis_zremrangebyscore("TS@" + hostID,
                                                      sortedTS[0],sortedTS[-1])
                redisCollector.redis_zremrangebyscore("DATAS@" + hostID,
                                                      sortedTS[0],sortedTS[-1])

        # Thread End
        sema.release()
        return True



    def startThreads(self):
        "Start threads"

        # If simulate open file and make Lock
        if self._simulate:
            simulateFileOpen = open(self._simulate_file,'a')
            self.verrou=threading.Lock()

        # Get all HOSTS
        allHosts={}
        writedHosts=[]
        numberOfThreads = 0
        random.shuffle(self._host_list)

        # threads configuration
        signal.signal(signal.SIGINT, self.sighandler)
        # Max de threads
        sema = threading.BoundedSemaphore(value=self._storage_thread)
        threads = []

        # For each collector
        for collectorLine in self._host_list:
            needThreads = 0
            collectorHosts = self.getHostList(collectorLine)

            numberOfHosts = len(collectorHosts)
            allHosts[collectorLine['host']]=collectorHosts
            writedHosts.extend(collectorHosts)
            # Get number of threads for this collector
            needThreads =  math.ceil((numberOfHosts+0.0) /
                                      self._max_hosts_by_thread)

            # Start each threads for this collector
            for i in range(int(needThreads)): 
                numberOfThreads = numberOfThreads + 1
                threadId = numberOfThreads

                # Get thread host list
                hostMin    = i*self._max_hosts_by_thread
                hostMax    = hostMin + self._max_hosts_by_thread
                threadHostListe = collectorHosts[hostMin:hostMax]

                # start thread
                self._logger.debug("Start thread " + str(numberOfThreads) 
                    + "  --  min : "  + str(hostMin)
                    + " / max : "     + str(hostMax)
                    + " / args : "    + str(threadHostListe))
                sema.acquire()
                if self._sigint:
                    sys.exit()
                    
                if not self._simulate:
                    t = threading.Thread(target=self.worker,
                                         args=(threadId, sema,
                                               collectorLine, threadHostListe))
                else:
                    t = threading.Thread(target=self.worker,
                                         args=(threadId, sema,collectorLine,
                                               threadHostListe,
                                               simulateFileOpen))
                t.setDaemon(True) # thread non bloquante
                t.start()
                threads.append(t)

        self._logger.debug("Thread - Max hosts by thread : "
            + str(self._max_hosts_by_thread))
        self._logger.debug("Thread - Max concurrency thread : "
            + str(self._storage_thread))
        self._logger.debug("Thread - Number of collector : "
            + str(self._host_listNumber))
        self._logger.debug("Thread - Number of threads : "
            + str(numberOfThreads))

        # Clean hosts
        self.cleanHosts(writedHosts)
        # Clean old wsp
        self.cleanOldWSP()

        # Wait des threads avec timeout self._thread_wait_timeout
        i=1
        for thread in threads:
            if ( self._thread_wait_timeout > 0 ):
                thread.join(self._thread_wait_timeout)
                if thread.isAlive():
                    self._logger.critical("Thread " + str(i) 
                                        + " timeout : " + str(i)
                                        + "/" + str(int(numberOfThreads)))
            else :
                thread.join()
            self._logger.warning("Thread finished : " + str(i)
                               + "/" + str(int(numberOfThreads)))
            i+=1

        return True




