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
        """Return for all datas you have collected. The output must be formated
           like that : ::

             infos=   [{    'Plugin': plugin,
                           'Base': '1000',
                           'Describ': '',
                           'Title': plugin,
                           'Vlabel': '',
                           'Order': '',
                           'Infos': {
                                 "id":{"type": "COUNTER", "id": "down", "label": "received"},
                                 "id":{"type": "COUNTER", "id": "up", "label": "upload"},
                      }]

           .. warning::

             Each DataSource (each datas) you define in getData must have at
             least an entry in getInfo return like ``"id":{"id": "up"}``
        """
        raise NotImplementedError



    def getData(self):
        """Get and return all collected datas. The output must be formated
           like that : ::

             data=   [{      'TimeStamp': 1410907894,
                             'Plugin': 'df',
                             'Values': {
                                         'dev_sda' : 40,
                                         'dev_sdb' : 15,
                                       }
                     }]

        """
        raise NotImplementedError


