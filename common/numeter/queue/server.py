from oslo.config import cfg
from oslo import messaging
import eventlet
import logging

LOG = logging.getLogger(__name__)

class OverrideMessageHandlingServer(messaging.server.MessageHandlingServer):
    "override MessageHandlingServer to bind multiple topics"
    def start(self):
        if self._executor is not None:
            return

        try:
            listener = self.transport._listen(self.target)
        except driver_base.TransportDriverError as ex: 
            raise ServerListenError(self.target, ex) 

        for target in self.target.targets:
            listener.conn.declare_topic_consumer(target.topic,
                                                 listener,
                                                 ack_on_error=False,
                                                 queue_name=self.target.topic)

        self._executor = self._executor_cls(self.conf, listener,
                                            self.dispatcher)
        self._executor.start()


class Targets(messaging.Target):
    "Target objects with additionnal targets"
    def __init__(self,targets):
        self.targets = targets
        first_target = iter(self.targets).next()
        # Get first topic and server for old compatibilities
        topic = first_target.topic
        server = first_target.server
        super(Targets, self).__init__(topic=topic,server=server)


def _get_rpc_server(transport, target, endpoints,
                   executor='blocking', serializer=None):
    dispatcher = messaging.rpc.dispatcher.RPCDispatcher(endpoints, serializer)
    return OverrideMessageHandlingServer(transport, target,
                                            dispatcher, executor)


def get_rpc_server(topics, server, hosts, endpoints, password='guest'):
    eventlet.monkey_patch()
    conf = cfg.CONF
    conf.transport_url = 'rabbit://'
    conf.rabbit_hosts = hosts
    conf.rabbit_password = password
    conf.control_exchange = 'numeter'
    transport = messaging.get_transport(conf)
    # Default topic and queue_name
    targets = [messaging.Target(topic=server, server=server)]
    # Append topics
    for topic in topics:
        targets.append(messaging.Target(topic=topic, server=server))
    return _get_rpc_server(transport, Targets(targets), endpoints, executor='blocking')
    #return _get_rpc_server(transport, Targets(targets), endpoints, executor='eventlet')

