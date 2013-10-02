import logging
LOG = logging.getLogger('numeter.storage.%s' % __name__)

class StorageEndpoint(object):

    def __init__(self, storage):
        self.storage = storage

    def ping(self, ctxt, args):
        print 'Recev'
        print str(ctxt)
        print '%s' % str(args)
        if args['fail']:
            print 'Message fail'
            raise Exception('message')
        return 'Pong'

    def poller_msg(self, ctxt, args):
        LOG.info('Recev message')
        LOG.debug('Message context' % (ctxt))
        LOG.debug('Message args : %s' % str(args))
        msg_type = ctxt.get('type', None)
        if msg_type == 'data':
            self._call_write_data(ctxt, args)
        elif msg_type == 'info':
            self._call_write_info(ctxt, args)
        else:
            LOG.warning('Unable to get message type, ignore this message')
            raise Exception('message')

    def _call_write_data(self, ctxt, args):
        LOG.debug('Write data : %s' % ctxt['plugin'])
        LOG.debug('Message : %s -- %s' % (ctxt, args))
        data = args.get('message', None)
        plugin = ctxt.get('plugin', None)
        hostID = ctxt.get('hostid', None)
        self.storage._write_data(hostID, plugin, data)

    def _call_write_info(self, ctxt, args):
        LOG.debug('Write info : %s' % ctxt['plugin'])
        LOG.debug('Message : %s -- %s' % (ctxt, args))
        info = args.get('message', None)
        self.storage._write_info(ctxt['hostid'], info)

