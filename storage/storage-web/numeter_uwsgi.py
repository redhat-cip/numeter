#!/usr/bin/env python


from myRedisConnect import *
import ConfigParser
from flask import Flask, request
import json
import rrdtool
import os

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

# test url http://10.66.6.213:3031/hosts
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

# test url http://10.66.6.213:3031/hinfo?host=10.66.6.216
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

# test url http://10.66.6.213:3031/list?host=10.66.6.216
@app.route(baseURL + '/list', methods=['GET', 'POST'])
def list():
    if request.method == 'GET':
        if request.args.has_key("host") \
        and request.args["host"] != "":
            host = request.args["host"]
            myConnect = redisStartConnexion()
            response = myConnect.redis_hgetall("INFOS@"+host)
            #response = myConnect.redis_hkeys("INFOS@"+host)
            return  '{ "list":'+pythonToJson(response)+'}'
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


# Test url http://10.142.32.75:8080/numeter-storage/data?host=127.0.0.1&plugin=cpu&ds=nice&res=Daily
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
                startPoint = '-24h'
            elif resolution == "Weekly":
                startPoint = '-7day'
            elif resolution == "Monthly":
                startPoint = '-31day'
            elif resolution == "Yearly":
                startPoint = '-1y'

            # Fetch all ds :
            VALUES_JSON=[]
            for ds in allDS.split(','):

                # Fetch rrd
                # ((1335530280, 1335530640, 60), ('_dev_shm',), [(None,), (None,), (None,), (None,)])
                if os.path.isfile(str(path+'/'+plugin+'/'+ds+'.rrd')):
                    result_rrd = rrdtool.fetch( str(path+'/'+plugin+'/'+ds+'.rrd'),
                                            'AVERAGE', '-s '+startPoint, '-e N')
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
                for value in result_rrd[2]:
                    if value[0] == None:
                        tmp_data.append("null")
                    else:
                        tmp_data.append(value[0])
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


##!/usr/bin/env python
## -*- coding: utf8 -*-
#
#import os
#import json
#import re
#import sys
#import rrdtool
#import subprocess
#
#print sys.argv
#
#try:
#    host = sys.argv[1]
#    plugin = sys.argv[2]
#    allDS = sys.argv[3]
#    resolution = sys.argv[4]
#    #print "{'host':'"+host+"', 'plugin': '"+plugin+"', 'allDS': '"+allDS+"'}"
#except:
#    print "{}"
#    exit(0)
#
##print plugin
#
#process = subprocess.Popen("/usr/bin/redis-cli -a password HGET RRD_PATH "+host , shell=True, stdout=subprocess.PIPE)
#(result, stderr) = process.communicate()
#
#rrd_path=[]
#
#
## Pour chaques ds : 
#path = result.rstrip()
#for ds in allDS.split(','):
#    rrd_path.append(path+'/'+plugin+'/'+ds+'.rrd')
#
#if resolution == "Daily":
#    startPoint = '-24h'
#elif resolution == "Weekly":
#    startPoint = '-7day'
#elif resolution == "Monthly":
#    startPoint = '-31day'
#elif resolution == "Yearly":
#    startPoint = '-1y'
#
## Get values
#VALUES={}
#for rrds in rrd_path:
#    result_rrd = rrdtool.fetch(rrds, 'AVERAGE', '-s '+startPoint, '-e N')
#    #result_rrd = rrdtool.fetch(rrds, 'AVERAGE', '-s -1h', '-e N')
#    #result_rrd = rrdtool.fetch(rrds, 'AVERAGE', '-s -24h', '-e N')
#    #result_rrd = rrdtool.fetch(rrds, 'AVERAGE', '-s -24h', '-e N', '--resolution', '300')
#    #result_rrd = rrdtool.fetch(rrds, 'AVERAGE', '-s -6d', '-e N')
#    #result_rrd = rrdtool.fetch(rrds, 'AVERAGE', '-s -60min', '-e N')
#    TS_START = result_rrd[0][0]
#    TS_END = result_rrd[0][1]
#    TS_STEP = result_rrd[0][2]
#    DS = result_rrd[1][0]
#    VALUES[DS] = result_rrd[2]
#   
## Format all datas :
#formatedDatas = {}
#for (ds, values) in VALUES.items():
#    tmp_data="["
#    for value in values:
#        if value[0] == None:
#            tmp_data = tmp_data + "null,"
#        else:
#            tmp_data = tmp_data + str(value[0]) + ","
#    tmp_data = tmp_data.rstrip(",")
#    tmp_data = tmp_data + "]"
#    formatedDatas[ds] = tmp_data
#
#all_datas = ""
#for ds in VALUES.keys():
#    all_datas = all_datas + '\n    "'+ds+'" : '+formatedDatas[ds]+','
#all_datas = all_datas.rstrip(',')
#
## Make Json return :
#print '{'
#print '    "TS_start" : '+str(TS_START)+','
#print '    "TS_step" : '+str(TS_STEP)+','
#print '    "DATAS" : {'
#print all_datas
#print '    }'
#print '}'
#

#rrd_path = result.rstrip()+"/"+sys.argv[1]+"/_dev_simfs.rrd"

#print TS_START
#print TS_END
#print TS_STEP
#print DS
#print VALUES

#
##{
##    Plugin : "name",
##    Base : "...",
##    Title : "...",
##    Vlabel : "...",
##    Order : "...",
##    TS_start : "123456789",
##    TS_step : "60",
##    Infos : {
##        id : { label : "...", Type : "..."},
##        id : { label : "...", Type : "..."}
##    },
##    DATAS : {
##        id : [1,2,3,4,5,6,7,8,9],
##        id : [1,2,3,4,5,6,7,8,9]
##    }
##}
#
#
#
#
#
##result_rrd = rrdtool.info(rrd_path)
#
#
