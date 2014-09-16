#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ModulesGeneric(object):
    """Module generic is the skeleton to build your own numeter module.
        If you want to write your own numeter module, you can take this
        class and build your own with it.
    """

    def  __init__(self, configParser=None):
        """When numeter load a module, the only one parameter is the config
           parser. It's allow you to add section in numeter config file for your
           own module."""
        raise NotImplementedError

    def getInfo(self):
        "Return plugins info for refresh"
        raise NotImplementedError
#        infos=   [{    'Plugin': plugin,
#                      'Base': '1000',
#                      'Describ': '',
#                      'Title': plugin,
#                      'Vlabel': '',
#                      'Order': '',
#                      'Infos': {
#                            "id":{"type": "COUNTER", "id": "down", "label": "received"},
#                            "id":{"type": "COUNTER", "id": "up", "label": "upload"},
#
#                 }]
# /!\ Attention chaque DS doit avoir une entré dans Infos pour ne pas étre ignoré. par exemple "id":{"id": "up"} au moins !


    def getData(self):
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


