#!/usr/bin/env python

import socket

class MuninSock:

    def __init__(self):
        self._munin_host = "127.0.0.1"
        self._munin_port = 4949

    def __enter__(self):
        self.munin_sock = socket.create_connection((self._munin_host
                                            , self._munin_port))
        self._s = self.munin_sock.makefile()
        self.hello_string = self._s.readline().strip()
	return self.munin_sock

    def __exit__(self, type, value, traceback):
        self.munin_sock.close()


class MuninConnection:
    
    def __init__(self):
        self.watchdog = 1000 # watchdog for munin socket error

    def _readline(self):
        self._s = self.sock.makefile()
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
        with MuninSock() as self.sock:
            self.sock.sendall("list %s\n" % node)
            return_list = self._readline().split(' ')
        return return_list if return_list != [''] else []

    def munin_nodes(self):
        with MuninSock() as self.sock:
            self.sock.sendall("nodes\n")
            return_node = [ line for line in self._iterline() ]
        return return_node[0] if return_node else None

