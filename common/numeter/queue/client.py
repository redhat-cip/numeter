from oslo import messaging
from oslo.config import cfg
import logging

LOG = logging.getLogger(__name__)

class BaseAPIClient(messaging.RPCClient):
    def __init__(self, transport):
        target = messaging.Target(topic='default_topic')
        super(BaseAPIClient, self).__init__(transport, target)

    def ping(self, context, topic, args=None):
        print 'Launch ping topic=%s' % topic
        cctxt = self.prepare(topic=topic)
        #return cctxt.call(context,'ping', args=args)
        return cctxt.cast(context,'ping', args=args)

    def poller_msg(self, context, topic, args=None):
        LOG.info('Send message %s context %s' % (topic, context))
        cctxt = self.prepare(topic=topic)
        return cctxt.cast(context,'poller_msg', args=args)

def get_rpc_client(hosts=[], password='guest'):
    conf = cfg.CONF
    conf.transport_url = 'rabbit://'
    conf.rabbit_max_retries = 1
    conf.rabbit_hosts = hosts
    conf.rabbit_password = password
    transport = messaging.get_transport(conf)
    return BaseAPIClient(transport)
