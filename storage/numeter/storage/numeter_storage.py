#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import ConfigParser
import time
import os
import json
from numeter.redis import RedisConnect
from numeter.storage.numeter_storage_endpoints import StorageEndpoint
from numeter.queue import server as NumeterQueueC
#import socket
import re
import logging
import sys
#import MySQLdb
import math
import hashlib
import subprocess # Clean old wsp

#Python-whisper
import whisper


import pprint # Debug (dumper)

#
# Storage
#
class Storage(object):
    def __init__(self,configFile="/etc/numeter_storage.cfg"):

        # Default configuration
        self._enable                    = False
        self._logLevel                  = "debug"
        self._log_level_stdr            = "debug"
        self._log_path                  = "/var/log/cron_numeter.log"
        self._rpc_hosts                 = ["127.0.0.1"]
        self._rpc_password              = 'guest'
        self._host_list_file            = "/dev/shm/numeter_storage_host_list"
        self._redis_storage_port        = 6379
        self._redis_storage_timeout     = 10
        self._redis_storage_password    = None
        self._redis_storage_host        = "127.0.0.1"
        self._redis_storage_db          = 0
        self._redis_connexion           = None
        self._wsp_path                  = "/opt/numeter/wsp"
        self._wsp_path_md5_char         = 2
        self._wsp_clean_time            = 48 # 48h
        self._wsp_delete                = False
        self._host_list                 = []
        self._host_listNumber           = 0
        self._dataNumber                = 0
        self._pluginNumber              = 0
        self._sigint                    = False
        self._storage_name              = socket.gethostname()


        # Read de la conf
        self._configFile = configFile
        self.readConf()

    def startStorage(self):
        "Start storage"
        # storage enable ?
        if not self._enable:
            self._logger.warning("Numeter cron disable : "
                "configuration enable = false")
            exit(2)

        self._redis_connexion = self.redisStartConnexion()

        if self._redis_connexion._error:
            self._logger.critical("Redis storage connexion ERROR - "
                "Check redis access or password")
            exit(1)

        if not self._get_host_list():
            self._logger.critical("Numeter storage get host list fail")
            exit(1)

        # Time and thread param verification
        if not self.paramsVerification():
            self._logger.critical("Args verification error")
            exit(1)

        # start consumer
        self._queue_consumer = NumeterQueueC.get_rpc_server(
                                              topics=self._host_list,
                                              server=self._storage_name,
                                              endpoints=[StorageEndpoint(self)],
                                              hosts=self._rpc_hosts,
                                              password=self._rpc_password)
        try:
            self._queue_consumer.start()
        except KeyboardInterrupt:
            self._queue_consumer.stop()
            #raise Exception('test catch')

        # End log time execution
        self._logger.warning("---- End : numeter_storage, %s host, %s "
                             " Plugins, %s Datas"
                             % (self._host_listNumber,
                                self._pluginNumber,
                                self._dataNumber))



    def redisStartConnexion(self):
        # Open redis connexion
        redis_connection = RedisConnect(host=self._redis_storage_host,
                                  port=self._redis_storage_port,
                                  socket_timeout=self._redis_storage_timeout,
                                  db=self._redis_storage_db,
                                  password=self._redis_storage_password)
        if redis_connection._error:
            self._logger.critical("Redis server connexion ERROR - "
                + "Check server access or the password")
            exit(1)
        return redis_connection


    def getgloballog(self):
        "Init du logger (fichier et stdr)"
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




    def _get_host_list(self):
        "Get host list"
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
        if not self._host_listNumber > 0:
            self._logger.critical("paramsVerification Arg "
                "hostListNumber : Error (must be >0)")
            return False
        self._logger.debug("Threads paramsVerification : OK")
        return True


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
        for ds_name, value in data.get("Values", {}).iteritems():

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
        self._dataNumber += 1
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
        """info = {    'Plugin': plugin,
                       'Base': '1000',
                       'ClientHash': 'md5(client)', <---- add by this function (in MyInfo)
                       'Describ': '',
                       'Title': plugin,
                       'Vlabel': '',
                       'Order': '',
                       'Infos': {
                            "down" : {"type": "COUNTER", "id": "down", "label": "received"},
                             "up" : {"type": "COUNTER", "id": "up", "label": "upload"},
                        }
                  }"""
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
        self._pluginNumber += 1
        return True


    # TODO reimplement this (deprecated)
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


    # TODO reimplement this (deprecated)
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


    # TODO reimplement this (deprecated)
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
        # rpc_password
        if self._configParse.has_option('global', 'rpc_password') \
        and self._configParse.get('global', 'rpc_password'):
            self._rpc_password = self._configParse.get('global', 'rpc_password')
            self._logger.info("Config : rpc_password = %s" % self._rpc_password)

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
