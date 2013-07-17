#!/usr/bin/env python
import logging

from mykombu import NumeterQueueC

def mycallback(body, message):
    print "mycallback %s" % body
    message.ack() 

# Init logging level
logging.getLogger('numeterQueue').setLevel(logging.CRITICAL)

# Add handler for debug
logging.getLogger('numeterQueue').setLevel(logging.INFO)
logging.getLogger('numeterQueue').addHandler(logging.StreamHandler())

q = NumeterQueueC(pool=['amqp://rabbit1:5672//', 'amqp://rabbit2:5672//'],
             pooltype='F',
             exchanger='ex', type='direct',
             queue="ex_queue")
#q._callback = mycallback
q.recv(callback=mycallback)
#try:
#    q.recv('hello')
#except:
#    logging.critical("Recv message error")
