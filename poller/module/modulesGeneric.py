#!/usr/bin/env python
# -*- coding: utf8 -*-

import time

class modulesGeneric: 
    "Module generic"

    def  __init__(self,logger,configParser=None): raise NotImplementedError
    "Load configuration and start connexion"
    
    def pluginsRefresh():
        "Return plugins info for refresh"
        raise NotImplementedError
#        infos=   {    'Plugin': plugin, 
#                      'Base': '1000', 
#                      'Describ': '', 
#                      'Title': plugin, 
#                      'Vlabel': '', 
#                      'Order': '', 
#                      'Infos': {
#                            "id":{"type": "COUNTER", "id": "down", "label": "received"},
#                            "id":{"type": "COUNTER", "id": "up", "label": "upload"},
#                       
#                 }
# /!\ Attention chaque DS doit avoir une entré dans Infos pour ne pas étre ignoré. par exemple "id":{"id": "up"} au moins !


    def getData():
        "get and return all data collected"
        raise NotImplementedError
#        data=   [{      'TimeStamp': nowTimestamp, 
#                        'Plugin': 'df', 
#                        'Values': {
#                                    'dev_sda' : 40,
#                                    'dev_sdb' : 15,
#                                  }
#                }]
#        now              = time.strftime("%Y %m %d %H:%M", time.localtime())
#        nowTimestamp     = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M')) # "%.0f" % supprime le .0 aprés le














