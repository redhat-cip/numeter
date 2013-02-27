#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import time
import os
import json
from myRedisConnect import *
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
import subprocess # Clean old rrd

#Python-pyrrd
#from pyrrd.rrd import RRD, RRA, DS 

#Python-rrdtool
import rrdtool


import pprint # Debug (dumper)


#
# NEED apt-get install python-mysqldb python-rrdtool
#


#Chargement de la liste de cache md5
# Storage ajouter dans les conf la policy rra
# X Connexion aux redis collectors
# X Recupération de la liste des hosts
# X Pour chaque hosts : 
#    Get des infos myhost
#-----------------------
#    Pour chaque plugin :
#        Pour chaque plugin / infos 
#            Mettre a jour la base
#    Get la liste des TS à prendre
#    Lecture des data entre les TS trouvé + stocké dans un hash plug[name][idval].append(ts:value)
#    For each plugin:
#        Verif si le rrd_plugin_path existe si non le creer
#        Avant l'update d'un ID verif si rrdpath/plugin/rrd existe. Si non creer le rrd
#        C'est une valeur qui n'a pas d'infos alors pas prise en compte.
#        update des rrd rrdpath[host@plugin@valudID] avec les value dans plug[name][idval]
#    suppression des datas


#Penser de l'autre sens get les datas et créer les rrd puis aprés les infos ?

#TODO check redis messaging
#redisq resq 



#"{\"Description\": \"\", \"Client\": \"not assigned\", \"Name\": \"numeter-host-3\", \"Plugin\": \"MyInfo\"}"

#{"Describ": "",
# "Title": "Disk usage in percent",
# "Plugin": "df",
# "Vlabel": "%",
# "Base": "1000",
# "Infos": [{"id": "_dev_simfs", "label": "/"},
#     {"id": "_lib_init_rw", "label": "/lib/init/rw"},
#     {"id": "_dev_shm", "label": "/dev/shm"}],
# "Order": ""}

#{\"Describ\": \"\",
# \"Title\": \"CPU usage\",
# \"Plugin\": \"cpu\",
# \"Vlabel\": \"%\",
# \"Base\": \"1000\",
# \"Infos\": [
#    {\"info\": \"CPU time spent handling \\\"batched\\\" interrupts\", \"draw\": \"STACK\", \"min\": \"0\", \"label\": \"softirq\", \"type\": \"DERIVE\", \"id\": \"softirq\"},
#    {\"info\": \"CPU time spent waiting for I/Ore is nothing else to do.\", \"draw\": \"STACK\", \"min\": \"0\", \"label\": \"iowait\", \"type\": \"DERIVE\", \"id\": \"iowait\"},
#    {\"info\": \"CPU time spent by the kernel in system activities\", \"draw\": \"AREA\", \"min\": \"0\", \"label\": \"system\", \"type\": \"DERIVE\", \"id\": \"system\"},
#    {\"info\": \"Idle CPU time\", \"draw\": \"STACK\", \"min\": \"0\", \"label\": \"idle\", \"type\": \"DERIVE\", \"id\": \"idle\"},
#    {\"info\": \"CPU time spent by normal programs and daemons\", \"draw\": \"STACK\", \"min\": \"0\", \"label\": \"user\", \"type\": \"DERIVE\", \"id\": \"user\"},
#    {\"info\": \"CPU time spent handling interrupts\", \"draw\": \"STACK\", \"min\": \"0\", \"label\": \"irq\", \"type\": \"DERIVE\", \"id\": \"irq\"},
#    {\"info\": \"The time that a virtual Clf was not running\", \"draw\": \"STACK\", \"min\": \"0\", \"label\": \"steal\", \"type\": \"DERIVE\", \"id\": \"steal\"},
#    {\"info\": \"CPU time spent by nice(1)d programs\", \"draw\": \"STACK\", \"min\": \"0\", \"label\": \"nice\", \"type\": \"DERIVE\", \"id\": \"nice\"}],
# \"Order\": \"system user nice idle iowait irq softirq\"}

#"{\"Describ\": \"\",
# \"Title\": \"eth1 traffic\",
# \"Plugin\": \"if_eth1\",
# \"Vlabel\": \"bits in (-) / out (+) per ${graph_period}\",
# \"Base\": \"1000\",
# \"Infos\": [
#    {\"type\": \"COUNTER\", \"id\": \"down\", \"label\": \"received\"},
#    {\"info\": \"Traffic of the eth1 interface. Unable to deiiropriate for the interface.\",\"type\": \"COUNTER\", \"id\": \"up\", \"label\": \"bps\"}],
#\"Order\": \"down up\"}"


#
# myCollector
#
class myStorage:
    def __init__(self,configFile="/etc/numeter_storage.cfg"):

        # Default configuration
        self._startTime                       = time.time()
        self._enable                          = False
        self._simulate                        = False
        self._logLevel                        = "debug"
        self._log_level_stdr                  = "debug"
        self._log_path                        = "/var/log/cron_numeter.log"
        self._simulate_file                   = "/tmp/numeter.simulate"
        self._storage_thread                  = 10
        self._max_hosts_by_thread             = 2
        self._max_data_by_hosts               = 20
        self._thread_wait_timeout             = 60
        self._collector_list_type             = "file"
        self._collector_list_file             = "/dev/shm/numeter_storage_collector_list"
        self._collector_list_mysql_dbName     = "numeter"
        self._collector_list_mysql_dbUser     = "numeter"
        self._collector_list_mysql_dbPassword = ""
        self._collector_list_mysql_host       = "127.0.0.1"
        self._collector_list_mysql_port       = 3306
        self._collector_list_mysql_query      = "SELECT hostname,password FROM hosts"
        self._redis_storage_port              = 6379
        self._redis_storage_timeout           = 10
        self._redis_storage_password          = None
        self._redis_storage_host              = "127.0.0.1"
        self._redis_storage_db                = 0
        self._rrd_path                        = "/opt/numeter/rrd"
        self._rrd_module                      = "rrdtool"
        self._rrd_path_md5_char               = 2
        self._rrd_clean_time                  = 48 # 48h
        self._rrd_delete                      = False
        self._redis_collector_port            = 6379
        self._redis_collector_timeout         = 10
        self._collectorList                   = []
        self._collectorListNumber             = 0
        self._hostNumber                      = 0
        self._dataNumber                      = 0
        self._pluginNumber                    = 0
        self._sigint                          = False


        # Read de la conf
        self._configFile = configFile
        self.readConf()


    def startStorage(self):
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

        if not self.getcollectorList():
            self._logger.critical("Numeter storage get collector list fail")
            exit(1)

        # Time and thread param verification
        if not self.paramsVerification():
            self._logger.critical("Args verification error")
            exit(1)

        # Start threads
        self.startThreads()

        # End log time execution
        self._logger.warning("---- End : numeter_storage, "
            + str(self._collectorListNumber) + " collector, "
            + str(self._hostNumber) + " Hosts, "
            + str(self._pluginNumber) + " Plugins, "
            + str(self._dataNumber) + " Datas in "
            + str(time.time()-self._startTime) + ", seconds.")



    def redisStartConnexion(self):
        # Open redis connexion
        redis_connexion = myRedisConnect(host=self._redis_storage_host,
                                  port=self._redis_storage_port,
                                  socket_timeout=self._redis_storage_timeout,
                                  db=self._redis_storage_db,
                                  password=self._redis_storage_password)
        if redis_connexion._error:
            self._logger.critical("Redis server connexion ERROR - "
                + "Check server access or the password")
            exit(1)
        return redis_connexion


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

        # collector_list_type
        if self._configParse.has_option('global', 'collector_list_type') \
        and self._configParse.get('global', 'collector_list_type'):
            self._collector_list_type = self._configParse.get('global',
                                            'collector_list_type')
            self._logger.info("Config : collector_list_type = "
                + self._collector_list_type)

        # collector_list_file
        if self._configParse.has_option('global', 'collector_list_file') \
        and self._configParse.get('global', 'collector_list_file'):
            self._collector_list_file = self._configParse.get('global', 'collector_list_file')
            self._logger.info("Config : collector_list_file = "+self._collector_list_file)

        # collector_list_mysql_dbName
        if self._configParse.has_option('global', 'collector_list_mysql_dbName') \
        and self._configParse.get('global', 'collector_list_mysql_dbName'):
            self._collector_list_mysql_dbName = self._configParse.get('global', 'collector_list_mysql_dbName')
            self._logger.info("Config : collector_list_mysql_dbName = "+self._collector_list_mysql_dbName)
        # collector_list_mysql_dbUser
        if self._configParse.has_option('global', 'collector_list_mysql_dbUser') \
        and self._configParse.get('global', 'collector_list_mysql_dbUser'):
            self._collector_list_mysql_dbUser = self._configParse.get('global', 'collector_list_mysql_dbUser')
            self._logger.info("Config : collector_list_mysql_dbUser = "+self._collector_list_mysql_dbUser)
        # collector_list_mysql_dbPassword
        if self._configParse.has_option('global', 'collector_list_mysql_dbPassword') \
        and self._configParse.get('global', 'collector_list_mysql_dbPassword'):
            self._collector_list_mysql_dbPassword = self._configParse.get('global', 'collector_list_mysql_dbPassword')
            self._logger.info("Config : collector_list_mysql_dbPassword = "+self._collector_list_mysql_dbPassword)
        # collector_list_mysql_host
        if self._configParse.has_option('global', 'collector_list_mysql_host') \
        and self._configParse.get('global', 'collector_list_mysql_host'):
            self._collector_list_mysql_host = self._configParse.get('global', 'collector_list_mysql_host')
            self._logger.info("Config : collector_list_mysql_host = "+self._collector_list_mysql_host)
        # collector_list_mysql_query
        if self._configParse.has_option('global', 'collector_list_mysql_query') \
        and self._configParse.get('global', 'collector_list_mysql_query'):
            self._collector_list_mysql_query = self._configParse.get('global', 'collector_list_mysql_query')
            self._logger.info("Config : collector_list_mysql_query = "+self._collector_list_mysql_query)
        # collector_list_mysql_port
        if self._configParse.has_option('global', 'collector_list_mysql_port') \
        and self._configParse.getint('global', 'collector_list_mysql_port'):
            self._collector_list_mysql_port = self._configParse.getint('global', 'collector_list_mysql_port')
            self._logger.info("Config : collector_list_mysql_port = "+str(self._collector_list_mysql_port))

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

        # rrd_module
        if self._configParse.has_option('global', 'rrd_module') \
        and self._configParse.get('global', 'rrd_module'):
            self._rrd_module = self._configParse.get('global', 'rrd_module')
            self._logger.info("Config : rrd_module = "+self._rrd_module)
        # rrd_path
        if self._configParse.has_option('global', 'rrd_path') \
        and self._configParse.get('global', 'rrd_path'):
            self._rrd_path = self._configParse.get('global', 'rrd_path')
            self._logger.info("Config : rrd_path = "+self._rrd_path)
        # rrd_path_md5_char
        if self._configParse.has_option('global', 'rrd_path_md5_char') \
        and self._configParse.getint('global', 'rrd_path_md5_char'):
            self._rrd_path_md5_char = self._configParse.getint('global', 'rrd_path_md5_char')
            self._logger.info("Config : rrd_path_md5_char = "+str(self._rrd_path_md5_char))
        # rrd_delete
        if self._configParse.has_option('global', 'rrd_delete') \
        and self._configParse.getboolean('global', 'rrd_delete'):
            self._rrd_delete = self._configParse.getboolean('global', 'rrd_delete')
            self._logger.info("Config : rrd_delete = "+str(self._rrd_delete))
        # rrd_clean_time
        if self._configParse.has_option('global', 'rrd_clean_time') \
        and self._configParse.getint('global', 'rrd_clean_time'):
            self._rrd_clean_time = self._configParse.getint('global', 'rrd_clean_time')
            self._logger.info("Config : rrd_clean_time = "+str(self._rrd_clean_time))

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



    def getcollectorList(self):
        "Get collector list"
        self._collectorList = []
        # Mode file
        if self._collector_list_type == "file":
            try:
                # Open file
                collectorfile = open(self._collector_list_file)
                # Parse result
                regex = r"^([a-zA-Z0-9\.\-\_]+) *(:([0-9]+) *(:(.+))?)?$"
                for line in collectorfile.readlines():
                    if re.match(regex, line):
                        result = re.match(regex, line)
                        if result.group(3) != None and result.group(5) != None:
                            self._collectorList.append({'host':result.group(1),
                                'db':result.group(3),
                                'password':result.group(5)})
                        elif result.group(3) != None:
                            self._collectorList.append({'host':result.group(1),
                                'db':result.group(3)})
                        else:
                            self._collectorList.append({'host':result.group(1)})
                        self._collectorListNumber += 1
                # Close file
                collectorfile.close()
            except IOError, e:
                self._logger.critical("Open collector_list file Error "
                    + str(e))
                sys.exit (1)

            self._logger.info("Read file " + self._collector_list_file + " : OK")
            self._logger.info("File number of collector : "
                + str(self._collectorListNumber))


        # Mode mysql
        elif self._collector_list_type == "mysql":
            try:
                conn = MySQLdb.connect (host = self._collector_list_mysql_host,
                                 port = self._collector_list_mysql_port,
                                 user = self._collector_list_mysql_dbUser,
                                 passwd = self._collector_list_mysql_dbPassword,
                                 db = self._collector_list_mysql_dbName)
            except MySQLdb.Error, e:
                self._logger.critical("Error %d: %s" % (e.args[0], e.args[1]))
                sys.exit (1)
            self._logger.info("Connect to MySQL server on "
                + self._collector_list_mysql_host + " : OK")
            # Get all collectors
            cursor = conn.cursor ()
            cursor.execute (self._collector_list_mysql_query)
            collectorList_tmp = cursor.fetchall()
            self._collectorListNumber = cursor.rowcount;
            cursor.close ()
            conn.close ()
            # Format result
            for row in collectorList_tmp:
                if len(row)>1 and row[1] != None and row[1] != '' \
                and len(row)>2 and row[2] != None and row[2] != '':
                    self._collectorList.append({'host': row[0], 'db': row[1],
                                              'password': row[2]})
                elif len(row)>1 and row[1] != None and row[1] != '':
                    self._collectorList.append({'host': row[0] , 'db': row[1]})
                else:
                    self._collectorList.append({'host': row[0]})
            self._logger.info("MySQL number of collector : "
                + str(self._collectorListNumber))

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
        if not self._collectorListNumber > 0:
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



    def writePyrrd(self, sortedTS, hostAllDatas, host, baseRRDPath):
        "Write rrd with python-pyrrd"

        # For each plugin
        for plugin in hostAllDatas["Infos"]:
            if plugin == "MyInfo":
                continue

            rrdOpen=None

            # For each DS
            if not hostAllDatas["Infos"][plugin].has_key("Infos"):
                self._logger.error("writePyrrd host : " + host 
                    + " Plugin : " + plugin
                    + " don't have Infos, can't write data")
                continue
            for DSname in hostAllDatas["Infos"][plugin]["Infos"]:
                DSname = str(DSname)

                # Create rrd file - config rrd here
                rrdPath = str(baseRRDPath+"/"+plugin)

                if not os.path.isfile(rrdPath+"/"+DSname+".rrd"):
                    self._logger.warning("writePyrrd host : " + host 
                        + " Create rrd file : "+rrdPath+"/"+DSname+".rrd")
                    dss = []
                    rras = []
                    # Add DS
                    DStype =  str(hostAllDatas["Infos"][plugin]["Infos"][DSname].get("type","GAUGE"))
                    # Check rrd type
                    if  DStype != "GAUGE" and DStype != "COUNTER" \
                    and DStype != "DERIVE" and DStype != "ABSOLUTE" :
                        DStype = "GAUGE"
                    RRDheartbeat = 160
                    RRDstep=60
                    RRAxff=0.5
                    # Fixe ERROR: Invalid DS name for long ds name
                    ds = DS(dsName='42', dsType=DStype, heartbeat=RRDheartbeat)
#                    ds = DS(dsName=DSname, dsType=DStype, heartbeat=RRDheartbeat)
                    dss.append(ds)
                    # add RRA
                    # --- Daily (1 Minute Average)
                    rra1     = RRA(cf='AVERAGE', xff=RRAxff, steps=1, rows=1440)
                    rra2     = RRA(cf='LAST', xff=RRAxff, steps=1, rows=1440)
                    rra3     = RRA(cf='MIN', xff=RRAxff, steps=1, rows=1440)
                    rra4     = RRA(cf='MAX', xff=RRAxff, steps=1, rows=1440)
                    rras.extend([rra1, rra2, rra3, rra4])
                    # --- Weekly (5 Minute Average)
                    rra1     = RRA(cf='AVERAGE', xff=RRAxff, steps=5, rows=2016)
                    rra2     = RRA(cf='LAST', xff=RRAxff, steps=5, rows=2016)
                    rra3     = RRA(cf='MIN', xff=RRAxff, steps=5, rows=2016)
                    rra4     = RRA(cf='MAX', xff=RRAxff, steps=5, rows=2016)
                    rras.extend([rra1, rra2, rra3, rra4])
                    # --- Monthly (10 Min Average)
                    rra1     = RRA(cf='AVERAGE', xff=RRAxff, steps=10, rows=4608)
                    rra2     = RRA(cf='LAST', xff=RRAxff, steps=10, rows=4608)
                    rra3     = RRA(cf='MIN', xff=RRAxff, steps=10, rows=4608)
                    rra4     = RRA(cf='MAX', xff=RRAxff, steps=10, rows=4608)
                    rras.extend([rra1, rra2, rra3, rra4])
                    # --- Yearly (1 Hour Average)
                    rra1     = RRA(cf='AVERAGE', xff=RRAxff, steps=60, rows=8784)
                    rra2     = RRA(cf='LAST', xff=RRAxff, steps=60, rows=8784)
                    rra3     = RRA(cf='MIN', xff=RRAxff, steps=60, rows=8784)
                    rra4     = RRA(cf='MAX', xff=RRAxff, steps=60, rows=8784)
                    rras.extend([rra1, rra2, rra3, rra4])
                    # Create directory
                    if not os.path.exists(rrdPath):
                        try:
                            os.makedirs(rrdPath)
                            self._logger.info("writePyrrd host : " + host \
                            + " make directory :" + rrdPath)
                        except OSError:
                            self._logger.error("writePyrrd host : " + host \
                            + " can't make directory :" + rrdPath)
                            continue
                    try:
                        # Create rrd
                        rrdOpen = RRD(rrdPath+"/"+DSname+".rrd", ds=dss,
                                     rra=rras, start=1178143200, step=RRDstep)
                        rrdOpen.create()
                    except Exception as e:
                        self._logger.error("writePyrrd host : " + host
                            + " Create rrd Error "
                            + str(e))
                        continue
                else :
                    try:
                        rdOpen = RRD(rrdPath+"/"+DSname+".rrd")
                        self._logger.debug("writePyrrd host : " + host 
                            + " Update rrd file : "+rrdPath)
                    except Exception as e:
                        # Add delete rrd if update error ? (bad format)
                        self._logger.error("writePyrrd host : " + host
                            + " Open rrd Error "
                            + str(e))
                        continue

                ## For each TS
                for TS in sortedTS:
                    # Add data in buffer
#                    if hostAllDatas["Datas"].has_key(plugin) \
#                    and hostAllDatas["Datas"][plugin].has_key(TS) \
#                    and hostAllDatas["Datas"][plugin][TS].has_key(DSname):
                    # Note : One DS so one value, if + DS use --template
                    try:
                        rrdOpen.bufferValue(TS,
                            str(hostAllDatas["Datas"][plugin][TS][DSname]))
                    except Exception as e:
                        self._logger.error("writePyrrd host : " + host
                            + " Update buffer Error "
                            + str(e))
                        continue
    
                #Updater du rrd
                try:
                    rrdOpen.update()
                except Exception as e:
                    self._logger.error("writePyrrd host : " + host
                        + " Update Error "
                        + str(e))
                    continue
        return True


    def writeRrdtool(self, sortedTS, hostAllDatas, host, baseRRDPath):
        "Write rrd with python-rrdtool"

        # For each plugin
        for plugin in hostAllDatas["Infos"]:
            if plugin == "MyInfo":
                continue

            rrdOpen=None

            # For each DS
            if not hostAllDatas["Infos"][plugin].has_key("Infos"):
                self._logger.error("writerrdtool host : " + host 
                    + " Plugin : " + plugin
                    + " don't have Infos, can't write data")
                continue
            for DSname in hostAllDatas["Infos"][plugin]["Infos"]:

                DSname = str(DSname)

                # Create rrd file - config rrd here
                rrdPath = str(baseRRDPath+"/"+plugin)
                if not os.path.isfile(rrdPath+"/"+DSname+".rrd"):
                    self._logger.warning("writerrdtool host : " + host 
                        + " Create rrd file : "+rrdPath+"/"+DSname+".rrd")

                    # Add DS
                    DStype = str(hostAllDatas["Infos"][plugin]["Infos"][DSname].get("type","GAUGE"))
                    if  DStype != "GAUGE" and DStype != "COUNTER" \
                    and DStype != "DERIVE" and DStype != "ABSOLUTE" :
                        DStype = "GAUGE"
                    RRDheartbeat = "160"
                    RRDstep = "60"
                    RRAxff = "0.5"
                    # Create directory
                    if not os.path.exists(rrdPath):
                        try:
                            os.makedirs(rrdPath)
                            self._logger.info("writerrdtool host : " + host \
                            + " make directory :" + rrdPath)
                        except OSError:
                            self._logger.error("writerrdtool host : " + host \
                            + " can't make directory :" + rrdPath)

                    # Create rrd
                    try:
                        rrdOpen = rrdtool.create(rrdPath+"/"+DSname+".rrd",
                         "--step", RRDstep, 
                         "--start", "1178143200",
                         "DS:42:"+DStype+":"+RRDheartbeat+":U:U", # Fixe ERROR: Invalid DS name for long ds name
                         # "DS:"+DSname+":"+DStype+":"+RRDheartbeat+":U:U",
                         "RRA:AVERAGE:"+RRAxff+":1:1440", # --- Daily (1 Minute Average)
                         "RRA:LAST:"+RRAxff+":1:1440",
                         "RRA:MIN:"+RRAxff+":1:1440",
                         "RRA:MAX:"+RRAxff+":1:1440",
                         "RRA:AVERAGE:"+RRAxff+":5:2016", # --- Weekly (5 Minute Average)
                         "RRA:LAST:"+RRAxff+":5:2016",
                         "RRA:MIN:"+RRAxff+":5:2016",
                         "RRA:MAX:"+RRAxff+":5:2016",
                         "RRA:AVERAGE:"+RRAxff+":10:4608", # --- Monthly (10 Min Average)
                         "RRA:LAST:"+RRAxff+":10:4608",
                         "RRA:MIN:"+RRAxff+":10:4608",
                         "RRA:MAX:"+RRAxff+":10:4608",
                         "RRA:AVERAGE:"+RRAxff+":60:8784", # --- Yearly (1 Hour Average)
                         "RRA:LAST:"+RRAxff+":60:8784",
                         "RRA:MIN:"+RRAxff+":60:8784",
                         "RRA:MAX:"+RRAxff+":60:8784")
                    except Exception as e:
                        self._logger.error("writerrdtool host : " + host
                            + " Create rrd Error "
                        + str(e))
                        continue

                #try: TODO clean this part
                #else :
                #    pass
                    #    rrdOpen = RRD(str(rrdPath+"/"+DSname+".rrd"))
                    #    self._logger.debug("writerrdtool host : " + host
                    #        + " Update rrd file : "+rrdPath)
                    #except Exception as e:
                    #    # Add delete rrd if update error ? (bad format) 
                    #    self._logger.error("writerrdtool host : " + host +" Open rrd Error "
                    #    +str(e) )
                    #    continue

                self._logger.info("writerrdtool host : " + host
                        + " Update rrd file : "+rrdPath+"/"+DSname+".rrd")

                ## For each TS
                rrdUpdateBuffer = []
                for TS in sortedTS:
                    # Add data in buffer
#                    if hostAllDatas["Datas"].has_key(plugin) \
#                    and hostAllDatas["Datas"][plugin].has_key(TS) \
#                    and hostAllDatas["Datas"][plugin][TS].has_key(DSname):
                        # Note : One DS so one value, if + DS use --template
                    try:
                        rrdUpdateBuffer.append(str(TS) + ':'
                            + str(hostAllDatas["Datas"][plugin][TS][DSname]))
                    except Exception:
                        continue

                self._logger.debug("writerrdtool host : " + host
                    + " Update rrd file : " + rrdPath + "/" + DSname
                    + " Datas : " + str(rrdUpdateBuffer))

                #Updater du rrd
                if rrdUpdateBuffer != []:
                    try:
                        rrdOpen = rrdtool.update(str(rrdPath+"/"+DSname+".rrd"),
                                     rrdUpdateBuffer)
                    except Exception as e:
                        self._logger.error("writerrdtool host : " + host
                            + " Error "
                            + str(e))
                        continue

        return True



    def getInfos(self,redisCollector,host):
        "get and write hosts infos from collector"

        # Init
        hostInfos={}
        # Writed Infos 
        writedInfos = []
        rrdPath     = None
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

        # Add HostIDMD5 to hostinfo (Used in rrdpath)
        hostID = hostInfos["MyInfo"]["ID"]
        hostIDHash = self._redis_connexion.redis_hget("HOST_ID",hostID)

        # Get md5sum cache
        if hostIDHash == None:
            hostIDHash = ""
            hostIDHash = hashlib.md5()
            hostIDHash.update(hostID)
            # Get X first char in md5 sum X=_rrd_path_md5_char 
            hostIDHash = hostIDHash.hexdigest()[0:self._rrd_path_md5_char]
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
        rrdPath = str(self._rrd_path + "/" + hostIDHash + "/"
                      + hostInfos["MyInfo"]["HostIDFiltredName"])

        self._redis_connexion.redis_hset("RRD_PATH", hostID, rrdPath)
        self._redis_connexion.redis_hset("HOSTS", hostID,
                                         self.pythonToJson(hostInfos["MyInfo"]))
        # MyInfo is not write in redis INFOS@... but it is use by writeRRD* so writedInfos.append
        writedInfos.append("MyInfo")
        #self._redis_connexion.redis_hset("INFOS@"+host, "MyInfo", self.pythonToJson(hostInfos["MyInfo"]))

        return writedInfos, hostInfos, rrdPath





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
        "Clean info in redis and rrd"
        # Get current plugin list
        currentPlugin = self._redis_connexion.redis_hkeys("INFOS@"+hostID)
        if currentPlugin == []:
            self._logger.info("Redis - Clean info -- nothing to do" )
            return
        # Get the gap
        toDelete=list(set(currentPlugin)-set(writedInfos))

        # Clean notify
        if not self._rrd_delete: 
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
            rrdPath = self._redis_connexion.redis_hget("RRD_PATH",hostID)
            if rrdPath == None:
                self._logger.error("Redis - Clean info -- "
                    + "Can't get rrd path for " + hostID + " stop")
                return
            if self._rrd_delete: # Erase rrd
                for plugin in toDelete:
                    self._logger.warning("Redis - Clean info -- delete "
                        + rrdPath + "/"+plugin)
                    # Delete plugin Infos
                    self._redis_connexion.redis_hdel("INFOS@"+hostID,plugin)
                    # Delete rrd
                    os.system("rm -Rf "+rrdPath+"/"+plugin)
            else: # Notify in redis
                for plugin in toDelete:
                    self._logger.info("Redis - Clean info -- "
                        + "notify DELETED_PLUGINS " + plugin )
                    # Delete plugin Infos
                    self._redis_connexion.redis_hdel("INFOS@"+hostID,plugin)
                    # Set notify
                    self._redis_connexion.redis_hset("DELETED_PLUGINS",hostID
                        + "@" + plugin, rrdPath + "/" + plugin)



    def cleanHosts(self,writedHosts):
        "Clean info in redis and rrd"
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
        if not self._rrd_delete: 
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
                rrdPath = self._redis_connexion.redis_hget("RRD_PATH",hostID)
                if rrdPath == None:
                    self._logger.error("Redis - Clean hosts -- "
                        + "Can't get rrd path for " + hostID + " stop")
                    continue

                if self._rrd_delete: # Erase rrd
                    self._logger.warning("Redis - Clean hosts -- delete rrd "
                        + rrdPath)
                    # Delete rrd
                    os.system("rm -Rf "+rrdPath)
                else: # Notify in redis
                    self._logger.info("Redis - Clean hosts -- "
                        + "notify DELETED_HOSTS " + hostID )
                    # Set notify
                    self._redis_connexion.redis_hset("DELETED_HOSTS", hostID,
                                                     rrdPath)

                # Delete related infos
                self._redis_connexion.redis_hdel("HOSTS",hostID)
                self._redis_connexion.redis_hdel("HOST_ID",hostID)
                self._redis_connexion.redis_hdel("RRD_PATH",hostID)
                # Delete infos
                for plugin in self._redis_connexion.redis_hkeys("INFOS@"
                                                                + hostID):
                     self._redis_connexion.redis_hdel("INFOS@" + hostID, plugin)


    def cleanOldRRD(self):
        "Clean old rrds"

        # Get last clean time
        lastFetch = self._redis_connexion.redis_get("LAST_RRD_CLEAN")
        now = time.strftime("%Y %m %d %H", time.localtime())
        # "%.0f" % supprime le .0 aprés le timestamp
        nowTimestamp = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H'))

        if lastFetch == None  \
        or (int(lastFetch)+(self._rrd_clean_time*60*60)) <= int(nowTimestamp) \
        or not re.match("^[0-9]{10}$",lastFetch):
            rrdDelete = []

            # Set the new time
            self._redis_connexion.redis_set("LAST_RRD_CLEAN",nowTimestamp)

            if not os.path.isdir(self._rrd_path):
                self._logger.warning("Clean old RRD -- path rrd "
                    + self._rrd_path + " not found")
                return []

            if self._rrd_delete: # Erase rrd

                # Delete rrd
                process = subprocess.Popen("find " + self._rrd_path 
                + " -mmin +" + str(self._rrd_clean_time*60) 
                + " -type f" 
                + " -print" 
                + " -delete" , shell=True, stdout=subprocess.PIPE)
                (result, stderr) =  process.communicate()
                self._logger.warning("Clean old RRD -- delete rrd : "
                    + str(result))
                rrdDelete = result.split()

                # Clean empty dirs
                process = subprocess.Popen("find " + self._rrd_path 
                + " -type d"
                + " -empty" 
                + " -print"
                + " -delete" , shell=True, stdout=subprocess.PIPE)
                (result, stderr) =  process.communicate()
                self._logger.warning("Clean old RRD -- delete empty dirs : "
                    + str(result))
                return rrdDelete

            else : # Just notify
                process = subprocess.Popen("find " + self._rrd_path
                    + " -mmin +" + str(self._rrd_clean_time*60)
                    + " -type f", shell=True, stdout=subprocess.PIPE)
                (result, stderr) =  process.communicate()
                self._logger.info("Clean old RRD -- notify OLD_RRD : "
                    + str(lastFetch))
                rrdDelete = result.split()
                self._redis_connexion.redis_set("OLD_RRD",
                                                self.pythonToJson(rrdDelete))
                return rrdDelete

        else :
            self._logger.info("Clean old RRD -- not this time. Last clean : "
                + str(lastFetch))
            return []




    def workerRedis(self,threadId, sema,collectorLine,hostsList=[],simulateFileOpen=None):
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
            (writedInfo, hostAllDatas["Infos"], hostRRDPath) = self.getInfos(redisCollector,hostID)
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
                # Write rrd
                if self._rrd_module == "pyrrd":
                    self._logger.info( "Worker " + str(threadId) + " host : "
                        + hostID + " writePyrrd")
                    self.writePyrrd(sortedTS, hostAllDatas, hostID, hostRRDPath)
                else:
                    self._logger.info( "Worker " + str(threadId) + " host : "
                        + hostID + " writeRrdtool")
                    self.writeRrdtool(sortedTS, hostAllDatas,
                                      hostID, hostRRDPath)
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
        random.shuffle(self._collectorList)

        # threads configuration
        signal.signal(signal.SIGINT, self.sighandler)
        # Max de threads
        sema = threading.BoundedSemaphore(value=self._storage_thread)
        threads = []

        # For each collector
        for collectorLine in self._collectorList:
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
                    t = threading.Thread(target=self.workerRedis,
                                         args=(threadId, sema,
                                               collectorLine, threadHostListe))
                else:
                    t = threading.Thread(target=self.workerRedis,
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
            + str(self._collectorListNumber))
        self._logger.debug("Thread - Number of threads : "
            + str(numberOfThreads))

        # Clean hosts
        self.cleanHosts(writedHosts)
        # Clean old rrd
        self.cleanOldRRD()

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




#
# Main
#
#if __name__ == "__main__":
#    storage = myStorage("/opt/numeter_storage/numeter_storage.cfg")
#    storage.startStorage()
#    #####storage = myStorage("/home/gael/Bureau/git/numeter/db/storage/numeter_storage.cfg")
#    exit(0)


