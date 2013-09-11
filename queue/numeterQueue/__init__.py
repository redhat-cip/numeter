#!/usr/bin/env python

# http://thoai-nguyen.blogspot.fr/2012/05/rabbitmq-exchange-queue-name-convention.html
# rabbitmq-plugins list
# rabbitmq-plugins enable ... (webapp mochiweb port 55672)
# http://www.rabbitmq.com/man/rabbitmqctl.1.man.html#set_user_tags
#rabbitmqctl add_user admin admin
#rabbitmqctl set_user_tags admin administrator
#rabbitmqctl list_users

#from kombu import Connection
#from kombu import Exchange, Queue
#
#from kombu import common
#
#from kombu.mixins import ConsumerMixin
#from kombu import Producer
#
#
#import random
#import logging
#
#
#
#class NumeterQueue:
#
#    def __init__(self, pool, pooltype,**args):
#        # Disable pika log
#        self._logger = logging.getLogger('numeterQueue')
#        self._pool = pool
#        self._pooltype = pooltype # L : load Balancing / F fail over
#        #self._debugmsg = ''
#        self._initCallback(**args)
#
#    def _declareQueueAndExchanger(self, connect):
#        return
#
#    # Use kombu pool and rename pool -> failover
#    def _connect(self):
#        if self._pooltype == 'L': # LB
#            poollist = list(self._pool) # make a copy
#            random.shuffle(poollist)
#        else:
#            poollist = self._pool
#        for host in poollist:
#            #self._debugmsg = host
#            #try:
#            #    self._logger.info("Try connect to node %s" % host)
#            #    connect = Connection(host)
#            #    self._declareQueueAndExchanger(connect)
#            #    return connect
#            #except:
#            #    self._logger.warning("Connection node %s failed" % host)
#            #    continue
#            connect = Connection(host)
#            self._declareQueueAndExchanger(connect)
#            return connect
#        self._logger.error("Node connection AllNodesFailed")
#        raise Exception("AllNodesFailed")
#
#    def _close(self,connect):
#        return connect.release()
#
#
#class NumeterQueueC(NumeterQueue):
#
#    def _initCallback(self,**args):
#        self._exchanger_name = args.get('exchanger', 'default')
#        self._exchanger_type = args.get('type', 'direct')
#        self._queue_name = args.get('queue', 'default')
#        self._queue_routing_key = args.get('routing_key', self._queue_name)
#
#    def _declareQueueAndExchanger(self, connect):
#        # Exchanger
#        self._exchanger = Exchange(self._exchanger_name, type=self._exchanger_type)
#        # Queue http://kombu.readthedocs.org/en/latest/reference/kombu.html?highlight=queue#queue
#        self.task_queues = Queue(name=self._queue_name, exchange=self._exchanger, routing_key=self._queue_routing_key)
#        #task_queues = [Queue('hipri', task_exchange, routing_key='hipri'),
#        #               Queue('midpri', task_exchange, routing_key='midpri'),
#        #               Queue('lopri', task_exchange, routing_key='lopri')]
#        # Exchanger
#        bound_exchange = self._exchanger(connect.channel())
#        bound_exchange.declare()
#        # Queue http://kombu.readthedocs.org/en/latest/reference/kombu.html?highlight=queue#queue
#        bound_Q = self.task_queues(connect.channel())
#        bound_Q.declare()
#
#    def _callback(self, body, message):
#        self._logger.info("[x] Received %r" % body)
#        message.ack()
#
#    def recv(self, callback=None):
#        if callback is None:
#            callback = self._callback
#
#        c = self._connect()
#        # Consumer http://kombu.readthedocs.org/en/latest/userguide/consumers.html
#        task_queues = self.task_queues
#        class C(ConsumerMixin):
#        
#            def __init__(self, connection):
#                self.connection = connection
#        
#            def get_consumers(self, Consumer, channel):
#                return [Consumer(queues=task_queues, callbacks=[self.on_message])]
#                # Different callbacks
#                #self.channel2 = default_channel.connection.channel()
#                #return [Consumer(default_channel, queues1,
#                #                 callbacks=[self.on_message]),
#                #        Consumer(self.channel2, queues2,
#                #                 callbacks=[self.on_special_message])]
#        
#            def on_message(self, body, message):
#                pass
#
#        # Launch and set callback function
#        try:
#            myC = C(c)
#            myC.on_message = callback
#            myC.run()
#        except KeyboardInterrupt:
#            print('bye bye')
#
#class NumeterQueueP(NumeterQueue):
#
#    def _initCallback(self,**args):
#        self._exchanger_name = args.get('exchanger', 'default')
#        self._exchanger_type = args.get('type', 'direct')
#
#    def _declareQueueAndExchanger(self, connect):
#        # Exchanger
#        self._exchanger = Exchange(self._exchanger_name, type=self._exchanger_type)
#        # Exchanger
#        bound_exchange = self._exchanger(connect.channel())
#        bound_exchange.declare()
##exchanger='default', type='direct'
#    def send(self, routing_key, message):
#        c = self._connect()
#
#        # Exchanger
#        bound_exchange = self._exchanger(c.channel())
#        bound_exchange.declare()
#
#        # Producer
#        P = Producer(c,
#                    exchange=self._exchanger,
#                    #routing_key=queue,
#                    routing_key=routing_key,
#                    serializer="json")
#                    #serializer='pickle')
#
#        P.publish(message, delivery_mode=1)
#        #P.publish(message+" - "+self._debugmsg, delivery_mode=1)
#        #PERSISTENT_DELIVERY_MODE = 2
#        #TRANSIENT_DELIVERY_MODE = 1
#        self._close(c)
#
#    def sendMany(self, routing_key, messages):
#        c = self._connect()
#        # Producer
#        P = Producer(c,
#                    exchange=self._exchanger,
#                    routing_key=routing_key,
#                    serializer="json")
#                    #serializer='pickle')
#        for message in messages:
#            # send message on queue
#            P.publish(message, delivery_mode=1)
#            #P.publish(message+" - "+self._debugmsg, delivery_mode=1)
#            #PERSISTENT_DELIVERY_MODE = 2
#            #TRANSIENT_DELIVERY_MODE = 1
#        self._close(c)
#
