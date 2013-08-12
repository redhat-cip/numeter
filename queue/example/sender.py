#!/usr/bin/env python
import random
import logging
import sys

from numeterQueue import NumeterQueueP

# Init logging level
logging.getLogger('numeterQueue').setLevel(logging.CRITICAL)

# Add handler for debug
logging.getLogger('numeterQueue').setLevel(logging.INFO)
logging.getLogger('numeterQueue').addHandler(logging.StreamHandler())

#q = NumeterQueueP(pool=['amqp://rabbit1:5672//', 'amqp://rabbit2:5672//'], pooltype='F', exchanger='ex', type='direct')
q = NumeterQueueP(pool=['amqp://localhost:5672//'], pooltype='F', exchanger='numeter', type='topic')

value = { 
    "INFO" : {
        "Category": "system",
        "Describ": "",
        "Title": "Uptime",
        "Plugin": "uptime",
        "Vlabel": "uptime in days",
        "Base": "1000",
        "Infos": {
            "uptime": {"draw": "AREA", "id": "uptime", "label": "uptime"}
        },
        "Order": ""
    },
    "DATA" : [
        { 
            "TS_start" : 1373968200,
            "TS_step" : 60,
            "DATAS" : {
                "uptime" : [454.03, 454.03, 454.04]
            }
        }
    ]
}
# TODO try null / None data
try:
    q.send('mypoller.DATA.df',value)
except:
    logging.critical("Send message error : %s" % str(sys.exc_info()))

#try:
#    messages = ["Many message","Many message2"]
#    messages = [ str(n) for n in range(1,100)]
#    q.sendMany('ex_queue',messages)
#except:
#    logging.critical("Send message error : %s" % str(sys.exc_info()))
