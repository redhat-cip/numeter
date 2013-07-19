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

q = NumeterQueueP(pool=['amqp://rabbit1:5672//', 'amqp://rabbit2:5672//'], pooltype='F', exchanger='ex', type='direct')

try:
    q.send('ex_queue',"My message")
except:
    logging.critical("Send message error : %s" % str(sys.exc_info()))

try:
    messages = ["Many message","Many message2"]
    messages = [ str(n) for n in range(1,100)]
    q.sendMany('ex_queue',messages)
except:
    logging.critical("Send message error : %s" % str(sys.exc_info()))
