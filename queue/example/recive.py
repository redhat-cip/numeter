#!/usr/bin/env python
import logging

from numeterQueue import NumeterQueueC

def mycallback(body, message):
    print "mycallback %s" % body
    #print "mycallback %s" % message.delivery_tag
#'delivery_tag', 'headers'
    message.ack() 

# Init logging level
logging.getLogger('numeterQueue').setLevel(logging.CRITICAL)

# Add handler for debug
logging.getLogger('numeterQueue').setLevel(logging.INFO)
logging.getLogger('numeterQueue').addHandler(logging.StreamHandler())

#q = NumeterQueueC(pool=['amqp://rabbit1:5672//', 'amqp://rabbit2:5672//'],
q = NumeterQueueC(pool=['amqp://localhost:5672//'],
             pooltype='F',
             exchanger='numeter', type='topic',
             queue="storage1",
             routing_key='*.*.*')
#q._callback = mycallback
q.recv(callback=mycallback)
#try:
#    q.recv('hello')
#except:
#    logging.critical("Recv message error")
