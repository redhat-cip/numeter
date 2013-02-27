#!/usr/bin/env python
# -*- coding: utf8 -*-
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
import pprint # Debug (dumper)

#
# myCollector
#
class myCollector:
    def __init__(self,configFile="/etc/numeter_collector.cfg"):

        # Default configuration
        self._startTime                  = time.time()
        self._enable                     = False
        self._simulate                   = False
        self._logger                     = None
        self._logLevel                   = "debug"
        self._log_level_stdr             = "debug"
        self._log_path                   = "/var/log/cron_numeter.log"
        self._simulate_file              = "/tmp/numeter.simulate"
#        self._cron_time                  = 60
        self._thread_wait_timeout        = 60
        self._concurrency_thread                = 10
        self._max_host_by_thread         = 20
#        self._cacti_poller_time          = 300
        self._max_data_collect_time      = 20
        self._host_list_type             = "file"
        self._host_list_all_refresh      = 300   
        self._host_list_file             = "/dev/shm/numeter_collector_host_list"
        self._host_list_mysql_dbName     = "numeter"
        self._host_list_mysql_dbUser     = "numeter"
        self._host_list_mysql_dbPassword = ""
        self._host_list_mysql_host       = "127.0.0.1"
        self._host_list_mysql_port       = 3306
        self._host_list_mysql_query      = "SELECT hostname,password FROM hosts"
        self._redis_server_host          = "127.0.0.1"
        self._redis_server_port          = 6379
        self._redis_server_timeout       = 5
        self._redis_server_db            = 0
        self._redis_server_password      = None
        self._munin_port                 = 4949
        self._munin_socket_timeout       = 5
        self._redis_client_port          = 6379
        self._redis_client_timeout       = 10
        self._hostList                   = []
        self._hostListNumber             = 0
        self._datasNumber                = 0
        self._pluginsNumber              = 0
        self._sigint                     = False
        # Default server_name : hostname
        self._server_name                = os.uname()[1]
        # Read configuration file
        self._configFile = configFile
        self.readConf()

    def startCollector(self):
        "Start the Collector"
        # Check that the collector is enabled
        if not self._enable:
            self._logger.warning("Numeter cron disable : "
                + "configuration enable = false")
            exit(2)
        if not self._simulate:
            # Open a connection to Redis
            self._logger.debug("Simulate=false : start redis connection")
            self._redis_connection = self.redisStartConnexion()

            if self._redis_connection._error:
                self._logger.critical("Redis server connection ERROR - "
                    + "Check server access or the password")
                exit(1)
        if not self.getHostsList():
            self._logger.critical("Numeter cron get hosts list fail")
            exit(1)
        # Verify time and thread parameters
        if not self.paramsVerification():
            self._logger.critical("Args verification error")
            exit(1)
        # Start threads
        self.startThreads()
        # End log time execution
        self._logger.warning("---- End : numeter_collector, "
            + str(self._pluginsNumber) + " plugins, "
            + str(self._hostListNumber) + " hosts, "
            + str(self._datasNumber) + " datas in "
            + str(time.time()-self._startTime) + ", seconds.")

    def redisStartConnexion(self):
        # Open redis connection
        redis_connection = myRedisConnect(host=self._redis_server_host, \
                                    port=self._redis_server_port, \
                                    socket_timeout=self._redis_server_timeout, \
                                    password=self._redis_server_password, \
                                    db=self._redis_server_db)
        if redis_connection._error:
            self._logger.critical("Redis server connection ERROR - "
                + "Check server access or the password")
            exit(1)
        return redis_connection

    def getgloballog(self):
        "Logger initialization (file and stdr)"
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
        if  self._configParse.has_option('global', 'log_path') \
        and self._configParse.get('global', 'log_path'):
            self._log_path = self._configParse.get('global', 'log_path')
        # log_level
        if  self._configParse.has_option('global', 'log_level') \
        and self._configParse.get('global', 'log_level'):
            self._logLevel = self._configParse.get('global', 'log_level')
        # log_level_stdr
        if self._configParse.has_option('global', 'log_level_stdr') \
        and self._configParse.get('global', 'log_level_stdr'):
            self._log_level_stdr = self._configParse.get('global', 'log_level_stdr')
        # Start logger
        self._logger = self.getgloballog()
        self._logger.info("----- Start Numeter Cron -----")
        # enable
        if  self._configParse.has_option('global', 'enable') \
        and self._configParse.getboolean('global', 'enable'):
            self._enable = self._configParse.getboolean('global', 'enable')
            self._logger.info("Config : enable = "+str(self._enable))
        else:
            self._logger.info("Config : enable = "+str(self._enable))
        # simulate
        if  self._configParse.has_option('global', 'simulate') \
        and self._configParse.getboolean('global', 'simulate'):
            self._simulate = self._configParse.getboolean('global', 'simulate')
            self._logger.info("Config : simulate = "+str(self._simulate))
        else:
            self._logger.info("Config : simulate = "+str(self._simulate))
        # simulate_file
        if  self._configParse.has_option('global', 'simulate_file') \
        and self._configParse.get('global', 'simulate_file'):
            self._simulate_file = self._configParse.get('global', 'simulate_file')
            self._logger.info("Config : simulate_file = "+self._simulate_file)
        # max_host_by_thread
        if  self._configParse.has_option('global', 'max_host_by_thread') \
        and self._configParse.getint('global', 'max_host_by_thread'):
            self._max_host_by_thread = self._configParse.getint('global',
                                           'max_host_by_thread')
            self._logger.info("Config : max_host_by_thread = "
                + str(self._max_host_by_thread))
        # concurrency_thread
        if  self._configParse.has_option('global', 'concurrency_thread') \
        and self._configParse.getint('global', 'concurrency_thread'):
            self._concurrency_thread = self._configParse.getint('global',
                                           'concurrency_thread')
            self._logger.info("Config : concurrency_thread = "
                + str(self._concurrency_thread))
        #  thread_wait_timeout
        if self._configParse.has_option('global', 'thread_wait_timeout') \
        and self._configParse.getint('global', 'thread_wait_timeout'):
            self._thread_wait_timeout = self._configParse.getint('global',
                                            'thread_wait_timeout')
            self._logger.info("Config : thread_wait_timeout = "
                + str(self._thread_wait_timeout))
        # server_name
        if  self._configParse.has_option('global', 'server_name') \
        and self._configParse.get('global', 'server_name'):
            self._server_name = self._configParse.get('global', 'server_name')
            self._logger.info("Config : server_name = "+self._server_name)
#        #  cacti_poller_time
#        if  self._configParse.has_option('global', 'cacti_poller_time') \
#        and self._configParse.getint('global', 'cacti_poller_time'):
#            self._cacti_poller_time = self._configParse.getint('global', 'cacti_poller_time')
#            self._logger.info("Config : cacti_poller_time = "+str(self._cacti_poller_time))
        #  max_data_collect_time
        if  self._configParse.has_option('global', 'max_data_collect_time') \
        and self._configParse.getint('global', 'max_data_collect_time'):
            self._max_data_collect_time = self._configParse.getint('global',
                                              'max_data_collect_time')
            self._logger.info("Config : max_data_collect_time = "
                + str(self._max_data_collect_time))
        # host_list_type
        if  self._configParse.has_option('global', 'host_list_type') \
        and self._configParse.get('global', 'host_list_type'):
            self._host_list_type = self._configParse.get('global',
                                       'host_list_type')
            self._logger.info("Config : host_list_type = "+self._host_list_type)
        # host_list_file
        if  self._configParse.has_option('global', 'host_list_file') \
        and self._configParse.get('global', 'host_list_file'):
            self._host_list_file = self._configParse.get('global',
                                       'host_list_file')
            self._logger.info("Config : host_list_file = "+self._host_list_file)
        # host_list_mysql_dbName
        if  self._configParse.has_option('global', 'host_list_mysql_dbName') \
        and self._configParse.get('global', 'host_list_mysql_dbName'):
            self._host_list_mysql_dbName = self._configParse.get('global',
                                               'host_list_mysql_dbName')
            self._logger.info("Config : host_list_mysql_dbName = "
                + self._host_list_mysql_dbName)
        # host_list_mysql_dbUser
        if  self._configParse.has_option('global', 'host_list_mysql_dbUser') \
        and self._configParse.get('global', 'host_list_mysql_dbUser'):
            self._host_list_mysql_dbUser = self._configParse.get('global',
                                               'host_list_mysql_dbUser')
            self._logger.info("Config : host_list_mysql_dbUser = "
                + self._host_list_mysql_dbUser)
        # host_list_mysql_port
        if  self._configParse.has_option('global', 'host_list_mysql_port') \
        and self._configParse.getint('global', 'host_list_mysql_port'):
            self._host_list_mysql_port = self._configParse.getint('global',
                                             'host_list_mysql_port')
            self._logger.info("Config : host_list_mysql_port = "
                + str(self._host_list_mysql_port))
        # host_list_mysql_dbPassword
        if  self._configParse.has_option('global', 'host_list_mysql_dbPassword') \
        and self._configParse.get('global', 'host_list_mysql_dbPassword'):
            self._host_list_mysql_dbPassword = self._configParse.get('global',
                                                   'host_list_mysql_dbPassword')
            self._logger.info("Config : host_list_mysql_dbPassword = "
                + self._host_list_mysql_dbPassword)
        # host_list_mysql_host
        if  self._configParse.has_option('global', 'host_list_mysql_host') \
        and self._configParse.get('global', 'host_list_mysql_host'):
            self._host_list_mysql_host = self._configParse.get('global',
                                             'host_list_mysql_host')
            self._logger.info("Config : host_list_mysql_host = "
                + self._host_list_mysql_host)
        # host_list_mysql_query
        if  self._configParse.has_option('global', 'host_list_mysql_query') \
        and self._configParse.get('global', 'host_list_mysql_query'):
            self._host_list_mysql_query = self._configParse.get('global',
                                              'host_list_mysql_query')
            self._logger.info("Config : host_list_mysql_query = "
                + self._host_list_mysql_query)
        # redis_server_host
        if  self._configParse.has_option('global', 'redis_server_host') \
        and self._configParse.get('global', 'redis_server_host'):
            self._redis_server_host = self._configParse.get('global',
                                          'redis_server_host')
            self._logger.info("Config : redis_server_host = "
                + self._redis_server_host)
        # redis_server_port
        if  self._configParse.has_option('global', 'redis_server_port') \
        and self._configParse.getint('global', 'redis_server_port'):
            self._redis_server_port = self._configParse.getint('global',
                                          'redis_server_port')
            self._logger.info("Config : redis_server_port = "
                + str(self._redis_server_port))
        #  redis_server_password
        if self._configParse.has_option('global', 'redis_server_password') \
        and self._configParse.get('global', 'redis_server_password'):
            self._redis_server_password = self._configParse.get('global',
                                              'redis_server_password')
            self._logger.info("Config : redis_server_password = "
                + self._redis_server_password)
        # redis_server_timeout
        if  self._configParse.has_option('global', 'redis_server_timeout') \
        and self._configParse.getint('global', 'redis_server_timeout'):
            self._redis_server_timeout = self._configParse.getint('global',
                                             'redis_server_timeout')
            self._logger.info("Config : redis_server_timeout = "
                + str(self._redis_server_timeout))
        # redis_server_db
        if  self._configParse.has_option('global', 'redis_server_db') \
        and self._configParse.getint('global', 'redis_server_db'):
            self._redis_server_db = self._configParse.getint('global',
                                        'redis_server_db')
            self._logger.info("Config : redis_server_db = "
                + str(self._redis_server_db))
        # munin_port
        if  self._configParse.has_option('client', 'munin_port') \
        and self._configParse.getint('client', 'munin_port'):
            self._munin_port = self._configParse.getint('client', 'munin_port')
            self._logger.info("Config : munin_port = "+str(self._munin_port))
        #  munin_socket_timeout
        if  self._configParse.has_option('client', 'munin_socket_timeout') \
        and self._configParse.getint('client', 'munin_socket_timeout'):
            self._munin_socket_timeout = self._configParse.getint('client',
                                             'munin_socket_timeout')
            self._logger.info("Config : munin_socket_timeout = "
                + str(self._munin_socket_timeout))
        # redis_client_port
        if  self._configParse.has_option('client', 'redis_client_port') \
        and self._configParse.getint('client', 'redis_client_port'):
            self._redis_client_port = self._configParse.getint('client',
                                          'redis_client_port')
            self._logger.info("Config : redis_client_port = "
                + str(self._redis_client_port))
        # redis_client_timeout
        if  self._configParse.has_option('client', 'redis_client_timeout') \
        and self._configParse.getint('client', 'redis_client_timeout'):
            self._redis_client_timeout = self._configParse.getint('client',
                                             'redis_client_timeout')
            self._logger.info("Config : redis_client_timeout = "
                + str(self._redis_client_timeout))

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

    def getHostsList(self):
        "Get host list"
        self._hostList = []
        # Mode file
        if self._host_list_type == "file":
            try:
                # Open file
                hostfile = open(self._host_list_file)
                # Parse result
                regex = r"^([a-zA-Z0-9\.\-\_]+) *(:([0-9]+) *(:(.+))?)?$"
                for line in hostfile.readlines():
                    if re.match(regex, line):
                        result = re.match(regex, line)
                        if result.group(3) != None and result.group(5) != None:
                            self._hostList.append({'host':result.group(1), 
                                'db':result.group(3),
                                'password':result.group(5)})
                        elif result.group(3) != None:
                            self._hostList.append({'host':result.group(1),
                                'db':result.group(3)})
                        else:
                            self._hostList.append({'host':result.group(1)})
                        self._hostListNumber += 1
                # Close file
                hostfile.close()
            except IOError, e:
                self._logger.critical("Open host_list file Error " + str(e))
                sys.exit(1)

            self._logger.info("Read file " + self._host_list_file + " : OK")
            self._logger.info("File number of hosts : "
                + str(self._hostListNumber))

        # Mode mysql
        elif self._host_list_type == "mysql":
            try:
                conn = MySQLdb.connect (host = self._host_list_mysql_host,
                                      port = self._host_list_mysql_port,
                                      user = self._host_list_mysql_dbUser,
                                      passwd = self._host_list_mysql_dbPassword,
                                      db = self._host_list_mysql_dbName)
            except MySQLdb.Error, e:
                self._logger.critical("Error %d: %s" % (e.args[0], e.args[1]))
                sys.exit (1)
            self._logger.info("Connect to MySQL server on "
                + self._host_list_mysql_host + " : OK")
            # Get all hosts
            cursor = conn.cursor ()
            cursor.execute (self._host_list_mysql_query)
            hostList_tmp = cursor.fetchall()
            self._hostListNumber = cursor.rowcount;
            cursor.close ()
            conn.close ()
            # Format result
            for row in hostList_tmp:
                if len(row)>1 and row[1] != None and row[1] != '' \
                and len(row)>2 and row[2] != None and row[2] != '':
                    self._hostList.append({'host': row[0] , 'db': row[1],
                        'password': row[2]})
                elif len(row)>1 and row[1] != None and row[1] != '':
                    self._hostList.append({'host': row[0] , 'db': row[1]})
                else:
                    self._hostList.append({'host': row[0]})
            self._logger.info("MySQL number of hosts : "
                + str(self._hostListNumber))

        return True

    def paramsVerification(self):
        "Args verification"
        if not self._concurrency_thread >= 1:
            self._logger.critical("paramsVerification Arg concurrency_thread : "
                + "Error (must be >=1)")
            return False
        if not self._max_host_by_thread >= 1:
            self._logger.critical("paramsVerification Arg max_host_by_thread : "
                + "Error (must be >=1)")
            return False
        if not self._hostListNumber > 0:
            self._logger.critical("paramsVerification Arg hostListNumber : "
                + "Error (must be >0)")
            return False
        self._logger.debug("Threads paramsVerification : OK")
        return True

    def sighandler(self,num, frame):
        "Start threads"
#        global self._sigint
        self._sigint = True
        self._logger.warning("Thread Get sighandler !")

    def workerGetLastFetch(self,pollerRedisConnect,threadId,host):
        "Return lastFetch, fetchEnd"
        # Init 
        fetchEnd  = None
        lastFetch = None
        lastFetch = pollerRedisConnect.redis_hget("SERVER",self._server_name)
        
        if lastFetch == None: # Default never fetched
            fetchEnd = pollerRedisConnect.redis_zrangebyscore("TimeStamp", 
                "(-inf", "+inf",start=0, num=self._max_data_collect_time)

            if fetchEnd == []:  # If empty next -> 
                self._logger.warning("Worker "+str(threadId) 
                    + " Redis client - connection OK for host : " + host
                    + " Last check : None  //  End check : None")
                lastFetch = fetchEnd = None
            else :
                self._logger.info("Worker " + str(threadId) 
                    + " Redis client - connection OK for host : " + host 
                    + " Last check : None  //  End check : "
                    + str(fetchEnd[-1]))
                lastFetch = "-inf" # Default TimeStamp
                fetchEnd = fetchEnd[-1]
        else:
            fetchEnd = pollerRedisConnect.redis_zrangebyscore("TimeStamp",
                "(" + str(lastFetch), "+inf", start=0,
                num=self._max_data_collect_time)
            if fetchEnd == []:  # If empty next -> 
                self._logger.warning("Worker "+str(threadId)
                    + " Redis client - connection OK for host : " + host
                    + " Last check : " + str(lastFetch)
                    + "  //  End check : None")
                lastFetch = fetchEnd = None
            else:
                self._logger.info("Worker " + str(threadId)
                    + " Redis client - connection OK for host : "
                    + host + " Last check : " + str(lastFetch)
                    + "  //  End check : "+str(fetchEnd[-1]))
                fetchEnd = fetchEnd[-1]

        return lastFetch,fetchEnd

    def workerFetchDatas(self, pollerRedisConnect, threadId, host, hostID,
                        lastFetch, fetchEnd):
        "Fetch and write data"
        # Check hostID 
        if not hostID:
            self._logger.warning("Worker " + str(threadId) 
                + " Write host " + host + " error no hostID")
            return False
        # Check param
        if lastFetch == None or fetchEnd == None:
            return False
        # Fetch datas
        hostDatas = pollerRedisConnect.redis_zrangebyscore("DATAS",
                    "(" + lastFetch, fetchEnd)

        simulateBuffer=[]
        # Format all data
        W_TS = {}
        for redisJSONdata in hostDatas:
            pythonData = self.jsonToPython(redisJSONdata)

            if not pythonData.has_key("TimeStamp") \
            or not pythonData.has_key("Plugin") \
            or not pythonData.has_key("Values") \
            or not re.match('[0-9]+',pythonData["TimeStamp"]):
                continue

            self._logger.info("Worker " 
                + str(threadId) 
                + " Write in redis server host " + host + " DATAS@" + hostID
                + "@"+pythonData["Plugin"] + "TS : "+pythonData["TimeStamp"])
            self._logger.debug("Worker "
                + str(threadId) + " Write in redis server " + host + " DATAS@"
                + hostID + "@"+pythonData["Plugin"] + "TS : "
                + pythonData["TimeStamp"] + " values : "
                + str(pythonData["Values"]))

            # Write data in server
            if not self._simulate:
                self._redis_connection.redis_zadd("DATAS@" + hostID,
                    redisJSONdata, pythonData["TimeStamp"])
            else :
                simulateBuffer.append("Worker "
                    + str(threadId) + " ###Write data : "
                    + "DATAS@" + hostID
                    + "  -> TS  " + pythonData["TimeStamp"]
                    + "   DATAS  ->  " + str(redisJSONdata) )
            # Get all writed timestamp
            W_TS[pythonData["TimeStamp"]] = pythonData["TimeStamp"]
            self._datasNumber = self._datasNumber + 1

        # Write all data
        if not self._simulate:
            for timeS in sorted(W_TS):  # Add timestamp to TS@hostname
                self._logger.info('Worker '
                    + str(threadId) + ' Redis server - ADD Timestamp : '
                    + timeS + ' in ' + 'TS@' + hostID)
                self._redis_connection.redis_zadd("TS@" + hostID, timeS , timeS )
            # Write hostname in HOSTS
            self._logger.info('Worker ' + str(threadId)
                + ' Redis server - ADD HOSTS : ' + host + "->" + hostID)
            self._redis_connection.redis_hset("HOSTS", host, hostID)

            # Write last fetched timestamp in client redis key SERVER
            self._logger.info("Worker " + str(threadId)
                + " Redis client - SET last fetch for " + self._server_name
                + " at : " + fetchEnd)
            pollerRedisConnect.redis_hset("SERVER",self._server_name,fetchEnd)
        else :
            for timeS in sorted(W_TS):  # Add timestamp to TS@hostname
                simulateBuffer.append("Worker " + str(threadId)
                    + " ###Write Redis server - ADD Timestamp : "
                    + timeS + ' in ' + 'TS@' + hostID )
            simulateBuffer.append("Worker " + str(threadId)
                + " ###Write Redis server - ADD HOSTS : " + host )
            simulateBuffer.append("Worker " + str(threadId)
                + " ###Write Client Last Fetch : "
                + self._server_name
                + " ->  " + fetchEnd )

        # If simulate so -> get lock and write in file
        if self._simulate:
            self.verrou.acquire()
            for line in simulateBuffer:
                simulateFileOpen.write(line+"\n")
            self.verrou.release()
        return True

    def workerFetchInfos(self,pollerRedisConnect,threadId,host):
        "Fetch and write data"
        # Get INFOS
        allInfos = pollerRedisConnect.redis_hgetall("INFOS")

        if allInfos == {}:
            return [], None

        simulateBuffer=[]
        writedInfos = []

        if not "MyInfo" in allInfos:
            self._logger.info("Worker " + str(threadId) + " Host : "
                + host + " Error no plugin MyInfo")
            return [], None

        MyInfo = self.jsonToPython(allInfos["MyInfo"])

        if not 'ID' in MyInfo:
            self._logger.info("Worker " + str(threadId) + " Host : " 
                + host + " Error no ID in plugin MyInfo")
            return [], None

        MyInfo['Address'] = host 
        hostID = MyInfo['ID']
        MyInfoJSON = self.pythonToJson(MyInfo)
        allInfos["MyInfo"] = MyInfoJSON

        for key,valueJson in allInfos.iteritems():
            self._pluginsNumber = self._pluginsNumber + 1
            self._logger.info("Worker " + str(threadId)
                + " Redis - update host " + host + " INFOS@" + hostID
                + " Plugin : " + key)
            self._logger.debug("Worker " + str(threadId)
                + " Redis - update host " + host + " INFOS@" + hostID
                + " Plugin : " + key+" Value : " + valueJson)
            writedInfos.append(key)
            # Write info in redis server
            if not self._simulate:
                self._redis_connection.redis_hset("INFOS@"
                    + hostID, key, valueJson)
            else :
                simulateBuffer.append("###Write INFOS : "
                    +"INFOS@" + hostID
                    + "  -> " + key
                    + "  ->  " + str(valueJson) )

        # If simulate so -> get lock and write in file
        if self._simulate:
            self.verrou.acquire()
            for line in simulateBuffer:
                simulateFileOpen.write(line+"\n")
            self.verrou.release()

        return writedInfos, hostID

    def workerCleanInfo(self,writedInfos,host,threadId):
        "Clean info in redis"
        # Get current plugin list
        currentPlugin = self._redis_connection.redis_hkeys("INFOS@" + host)
        if currentPlugin == []:
            self._logger.info("Worker " + str(threadId)
                + " Redis - Clean info -- nothing to do" )
            return
        # Get the gap
        toDelete = list(set(currentPlugin)-set(writedInfos))
        # Same list do nothing
        if toDelete == []:
            self._logger.info("Worker " + str(threadId)
                + " Redis - Clean info -- nothing to do : same Infos" )
            return
        else: # Erase some plugin
            self._logger.info("Worker " + str(threadId)
                + " Redis - Clean info -- clean plugins : " + str(toDelete))
            if self._simulate:
                self.verrou.acquire()
                for line in simulateBuffer:
                    simulateFileOpen.write("===== Clean INFOS@" + host
                        + " =====\n" + str(toDelete))
                self.verrou.release()
            else:
                for plugin in toDelete:
                     self._redis_connection.redis_hdel("INFOS@" + host, plugin)

    def cleanHosts(self):
        "Clean Hosts in redis"

        # Get hostListe
        allHosts = []
        for hostLine in self._hostList:
            allHosts.append(hostLine['host'])
        # Get current hosts list
        currentHosts = self._redis_connection.redis_hkeys("HOSTS")
        if currentHosts == []:
            self._logger.info("Clean info -- nothing to do" )
            return
        # Get the gap
        toDelete=list(set(currentHosts)-set(allHosts))
        # Same list do nothing
        if toDelete == []:
            self._logger.info("Clean Hosts -- nothing to do : same Hosts" )
            return
        else: # Erase some plugin
            self._logger.warning("Clean Hosts -- Delete hosts "
                + "+ datas + infos for : " + str(toDelete))
            if self._simulate:
                self.writeInSimulateFile("===== Clean HOST and INFOS@host =====")
                self.writeInSimulateFile(str(toDelete))
            else:
                # Delete hosts
                for host in toDelete:
                    self._redis_connection.redis_hdel("HOSTS", host)
                    # Delete Datas
                    self._redis_connection.redis_zremrangebyscore("DATAS@"
                        + host, '-inf', '+inf')
                    # Delete Infos
                    for plugin in self._redis_connection.redis_hkeys("INFOS@"
                                                                    + host):
                        self._redis_connection.redis_hdel("INFOS@"+host,plugin)

    def workerRedis(self,threadId, sema,myHosts,simulateFileOpen=None):
        "Thread"
        #time.sleep(0)  # Debug add time
        self._logger.debug("Thread worker " + str(threadId)
            + " with host : " + str(myHosts))
        for hostLine in myHosts:
            # Get password and db
            host        = hostLine['host']
            redis_pass  = None
            redis_db    = "0"
            if hostLine.has_key('db'):
                redis_db = hostLine['db']
            if hostLine.has_key('password'):
                redis_pass = hostLine['password']
            pollerRedisConnect = myRedisConnect(host=host,
                                    port=self._redis_client_port,
                                    socket_timeout=self._redis_client_timeout,
                                    password=redis_pass,db=redis_db)
            # If error goto next
            if pollerRedisConnect._error:
                self._logger.error("Worker " + str(threadId)
                    + " Redis client connection ERROR for host : " + host)
                continue
            # Get Last fetch (SERVER) and fetch new data
            hostDatas = {}
            # Get last fetch and fetch end
            (lastFetch, fetchEnd) = self.workerGetLastFetch(pollerRedisConnect,
                                        threadId,host)
            # Fetch data and info if the host have new datas
            if fetchEnd == None:
                self._logger.warning("Worker " + str(threadId)
                    + " Redis client - TimeStamp list for " + host
                    + " is Empty, don't fetch")
            else :
                # Fetch and write infos
                writedInfos = []
                hostID = None
                writedInfos, hostID = self.workerFetchInfos(pollerRedisConnect,
                                          threadId,host)
                self.workerCleanInfo(writedInfos,hostID,threadId)
                # Fetch and write datas
                self.workerFetchDatas(pollerRedisConnect, threadId, host,
                    hostID, lastFetch, fetchEnd)

        # Thread End
        sema.release()

    def startThreads(self):
        "Start threads"
        # If simulate open file and make Lock
        if self._simulate:
            simulateFileOpen = open(self._simulate_file,'a')
            self.verrou=threading.Lock()
        # Number of needed threads
        numberOfThreads = math.ceil((self._hostListNumber+0.0) /
                              self._max_host_by_thread)
        self._logger.debug("Thread - Max host by thread : "
            + str(self._max_host_by_thread))
        self._logger.debug("Thread - Max concurrency thread : "
            + str(self._concurrency_thread))
        self._logger.debug("Thread - Number of hosts : "
            + str(self._hostListNumber))
        self._logger.debug("Thread - Number of threads : "
            + str(numberOfThreads))
        # threads configuration
        signal.signal(signal.SIGINT, self.sighandler)
        # max numbers of threads
        sema = threading.BoundedSemaphore(value=self._concurrency_thread)
        threads = []
        # launch numbers of thread
        for threadId in range(int(numberOfThreads)):
            hostMin = threadId * self._max_host_by_thread
            hostMax = hostMin + self._max_host_by_thread
            threadHost = self._hostList[hostMin:hostMax]

            self._logger.debug("Start thread " + str(threadId) + "  --  min : "
                + str(hostMin) + " / max : " + str(hostMax) + " / args : "
                + str(threadHost))

           # Start threads
            sema.acquire()
            if self._sigint:
                sys.exit()
                
            if not self._simulate:
                t = threading.Thread(target=self.workerRedis,
                        args=(threadId, sema,threadHost))
            else:
                t = threading.Thread(target=self.workerRedis,
                        args=(threadId, sema,threadHost,simulateFileOpen))
            t.setDaemon(True) # thread non bloquante
            t.start()
            threads.append(t)

        # Clean HOSTS
        self.cleanHosts()

        # Wait for threads with timeout self._thread_wait_timeout
        i=1
        for thread in threads:
            if ( self._thread_wait_timeout > 0 ):
                thread.join(self._thread_wait_timeout)
                if thread.isAlive():
                    self._logger.critical("Thread " + str(i) + " timeout : "
                        + str(i) + "/" + str(int(numberOfThreads)))
            else :
                thread.join()
            self._logger.warning("Thread finished : "+str(i) + "/"
                + str(int(numberOfThreads)))
            i+=1

        return True
#
# Main
#
#if __name__ == "__main__":
#    collector = myCollector("/opt/numeter_collector/numeter_collector.cfg")
#    collector.startCollector()
##    collector = myCollector("/home/gael/Bureau/git/numeter/db/collector/numeter_collector.cfg")
#    exit(0)
