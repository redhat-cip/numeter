#!/usr/bin/env python
# -*- coding: utf-8 -*-

from myRedisConnect import myRedisConnect
import ConfigParser
from flask import Flask, request
import json
#import rrdtool
import whisper
import os
import time

baseURL="/numeter-storage"

def pythonToJson(data):
    "Convert python to json"
    try:
        jsonData = json.dumps(data)
    except:
        jsonData = {}
    return jsonData


def readConf(configFile):
    "Read configuration file"

    global redis_host
    global redis_port
    global redis_db
    global redis_password
    # Default values : 
    redis_host="127.0.0.1"
    redis_db = 0
    redis_password=None


    configParse = ConfigParser.RawConfigParser()
    if configParse.read(configFile) == []: # If empty or not exist
        exit(1)
    # redis_port
    if configParse.has_option('global', 'redis_storage_port') \
    and configParse.getint('global', 'redis_storage_port'):
        redis_port = configParse.getint('global', 'redis_storage_port')
    # redis_password
    if configParse.has_option('global', 'redis_storage_password') \
    and configParse.get('global', 'redis_storage_password'):
        redis_password = configParse.get('global', 'redis_storage_password')
    # redis_host
    if configParse.has_option('global', 'redis_storage_host') \
    and configParse.get('global', 'redis_storage_host'):
        redis_host = configParse.get('global', 'redis_storage_host')
    # redis_db
    if configParse.has_option('global', 'redis_storage_db') \
    and configParse.getint('global', 'redis_storage_db'):
        redis_db = configParse.getint('global', 'redis_storage_db')


def redisStartConnexion():
    "Open redis connexion"
    redis_connexion = myRedisConnect(host=redis_host, \
                                     port=redis_port, \
                                     db=redis_db, \
                                     password=redis_password)
    if redis_connexion._error:
        exit(1)
    return redis_connexion

def jsonToPython(data):
    "Convert json to python"
    try:
        pythonData = json.loads(data)
    except:
        pythonData = {}
    return pythonData

configFile = "/etc/numeter/numeter_storage.cfg"
readConf(configFile)


app = Flask(__name__)

@app.route(baseURL + '/')
def index(): return 'index pass'

# test url http://127.0.0.1:3031/hosts
@app.route(baseURL + '/hosts')
def hosts():
    myConnect = redisStartConnexion()
    response={}
    allhosts = myConnect.redis_hgetall("HOSTS")
    for addr,value in allhosts.iteritems():
        value = jsonToPython(value)
        value['address'] = addr
        response[addr] = value
    return pythonToJson(response)

# test url http://127.0.0.1:3031/hinfo?host=1350646673-fe526c202a1812c0640877cebe801cc3
@app.route(baseURL + '/hinfo', methods=['GET', 'POST'])
def hinfo():
    if request.method == 'GET':
        if request.args.has_key("host") and request.args.has_key("host") != "":
            host    = request.args["host"]
            myConnect = redisStartConnexion()
            response = myConnect.redis_hget("HOSTS",host)
            return response if response != None else "{}"
        else:
            response="Args error"
            return  response
    else:
        return "Error"

# test url http://127.0.0.1:3031/list?host=127.0.0.1
@app.route(baseURL + '/list', methods=['GET', 'POST'])
def list():
    if request.method == 'GET':
        if request.args.has_key("host") \
        and request.args["host"] != "":
            host = request.args["host"]
            myConnect = redisStartConnexion()
            plugins = myConnect.redis_hgetall("INFOS@"+host)
            #response = myConnect.redis_hkeys("INFOS@"+host)
            # Make JSON
            response = '{'
            for plugin, info in plugins.iteritems():
                response += '"%s": %s,' % (plugin, info)
            response = '%s}' % response[:-1]
        else:
            response="Args error"
        return  response
    else:
        return "Error"

@app.route(baseURL + '/info', methods=['GET', 'POST'])
def info():
    if request.method == 'GET':
        if request.args.has_key("host") and request.args.has_key("host") != ""\
        and request.args.has_key("plugin") and request.args.has_key("plugin") != "" :
            plugin  = request.args["plugin"]
            host    = request.args["host"]
            myConnect = redisStartConnexion()
            response = myConnect.redis_hget("INFOS@"+host, plugin)
            return response if response != None else "{}"
        else:
            response="Args error"
            return  response
    else:
        return "Error"


# Test url http://127.0.0.1:8080/numeter-storage/data?host=1350646673-fe526c202a1812c0640877cebe801cc3&plugin=cpu&ds=nice&res=Daily
@app.route(baseURL + '/data', methods=['GET', 'POST'])
def data():
    if request.method == 'GET':
        if request.args.has_key("host") \
        and request.args.has_key("plugin") \
        and request.args.has_key("ds") \
        and request.args.has_key("res"):
            host        = request.args["host"]
            plugin      = request.args["plugin"]
            allDS       = request.args["ds"]
            resolution  = request.args["res"]

            myConnect = redisStartConnexion()
            path = myConnect.redis_hget("RRD_PATH", host)

            # Set startpoint for resolution
            if resolution == "Daily":
                startPoint = 86400
            elif resolution == "Weekly":
                startPoint = 604800
            elif resolution == "Monthly":
                startPoint = 18748800
            elif resolution == "Yearly":
                startPoint = 224985600

            # Fetch all ds :
            VALUES_JSON=[]
            for ds in allDS.split(','):

                # Fetch rrd
                # ((1335530280, 1335530640, 60), ('_dev_shm',), [(None,), (None,), (None,), (None,)])
                if os.path.isfile(str(path+'/'+plugin+'/'+ds+'.wsp')):
                   result_rrd = whisper.fetch(str(path+'/'+plugin+'/'+ds+'.wsp'), time.time() - startPoint, time.time()) 
                else:
                    return "{}"

                # Get info
                TS_START = result_rrd[0][0]
                TS_END = result_rrd[0][1]
                TS_STEP = result_rrd[0][2]
                # Fixe ERROR: Invalid DS name for long ds name
                DS = ds
                #DS = result_rrd[1][0]

                # Format the list of value in [0,1,2,null]
                tmp_data=[]
                for value in result_rrd[1]:
                    if value == None:
                        tmp_data.append("null")
                    else:
                        tmp_data.append(value)
                # Trick for join null string and int
                joined_values = ', '.join(["%s" % el for el in tmp_data]) 
                # stock values
                VALUES_JSON.append('"' + DS + '" : [' + joined_values + ']')

            # Format all DS values in one json stack
            ALL_VALUES_JSON = ','.join(VALUES_JSON)

            # Make Json return :
            response = '{'
            response += '    "TS_start" : '+str(TS_START)+','
            response += '    "TS_step" : '+str(TS_STEP)+','
            response += '    "DATAS" : {'
            response += ALL_VALUES_JSON
            response += '    }'
            response += '}'

            return response

        else:
            response="Args error"
            return response
    else:
        return "Error"



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=3031,debug=True)

