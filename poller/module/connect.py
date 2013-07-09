#!/usr/bin/env python

import socket

class MuninSock:

    def __init__(self):
        #self._logger = logger
        #self._logger.info("Plugin Munin start")
        #self._configParser = configParser
        self._munin_host = "127.0.0.1"
        self._munin_port = 4949
        self._plugins_enable = ".*"
        #self.munin_connection = None

        #if configParser: self.getParserConfig()
        #self._logger.info("section myMuninModule : plugins_enable = "
        #                + self._plugins_enable)
        #self._logger.info("section myMuninModule : munin_host = "
        #                + self._munin_host)
        #self._logger.info("section myMuninModule : munin_port = "
        #                + str(self._munin_port))


    def __enter__(self):
        self.munin_sock = socket.create_connection((self._munin_host
                                            , self._munin_port))
        self._s = self.munin_sock.makefile()
        #self.hello_string = self._readline()
        self.hello_string = self._s.readline().strip()
	return self.munin_sock

    def __exit__(self, type, value, traceback):
        self.munin_sock.close()


class MuninConnection:
    
    def __init__(self):
        self.watchdog = 1000 # watchdog for munin socket error

    def _readline(self):
        return self._s.readline().strip()

    def _iterline(self):
        watchdog = self.watchdog
        while watchdog > 0:
            watchdog = watchdog - 1
            line = self._readline()
            if not line:
                break
            elif line.startswith('#'):
                continue
            elif line == '.':
                break
            yield line

    def munin_list(self):
        # Get node name
        node = self.munin_nodes()
        # Start munin connexion
        #c.munin_connect()
        with MuninSock() as self.sock:
            self.sock.sendall("list %s\n" % node)
            self._s = self.sock.makefile()
            return_list = self._readline().split(' ')
        # Close munin connexion to avoid fucked plugin
        #c.munin_close()
        return return_list if return_list != [''] else []

    def munin_nodes(self):
        # Start munin connexion
        #c.munin_connect()
        with MuninSock() as self.sock:
            self.sock.sendall("nodes\n")
            self._s = self.sock.makefile()
            return_node = [ line for line in self._iterline() ]
        # Close munin connexion to avoid fucked plugin
        #c.munin_close()
        return return_node[0] if return_node else None

