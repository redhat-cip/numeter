#!/usr/bin/env python

import socket
import re

class MuninSock:

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __enter__(self):
        self.munin_sock = socket.create_connection((self.host, self.port))
        _s = self.munin_sock.makefile()
        hello_string = _s.readline().strip()
        return self.munin_sock

    def __exit__(self, type, value, traceback):
        self.munin_sock.close()


class MuninConnection:
    
    def __init__(self, logger, munin_host="127.0.0.1", munin_port=4949):
        self.watchdog = 1000 # watchdog for munin socket error
        self.munin_host = munin_host
        self.munin_port = munin_port
        self._logger = logger

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

    def munin_fetch(self, key):
        with MuninSock(self.munin_host, self.munin_port) as sock:
            self._s = sock.makefile()
            sock.sendall("fetch %s\n" % key)
            ret = {}
            for line in self._iterline():
                match = re.match("^([^\.]+)\.value", line)
                if match is None: continue
                key = match.group(1)
                match = re.match("^[^ ]+\s+([0-9\.U-]+)$", line)
                if match is not None: value = match.group(1)
                else: value = 'U'
                ret[key] = value
        return ret

    def munin_list(self):
        # Get node name
        node = self.munin_nodes()
        with MuninSock(self.munin_host, self.munin_port) as sock:
            self._s = sock.makefile()
            sock.sendall("list %s\n" % node)
            return_list = self._readline().split(' ')
        return return_list if return_list != [''] else []

    def munin_nodes(self):
        with MuninSock(self.munin_host, self.munin_port) as sock:
            self._s = sock.makefile()
            sock.sendall("nodes\n")
            return_node = [ line for line in self._iterline() ]
        return return_node[0] if return_node else None

    def munin_config(self, key):
        with MuninSock(self.munin_host, self.munin_port) as sock:
            self._s = sock.makefile()
            sock.sendall("config %s\n" % key)
            ret = {}
            for line in self._iterline():
                if line.startswith('graph_'):
                    try:
                        key, value = line.split(' ', 1)
                        ret[key] = value
                    except ValueError:
                        self._logger.info("myMuninModule : skipped key %s" % key)
                else:
                    # less sure but faster
                    #key, rest = line.split('.', 1)
                    #prop, value = rest.split(' ', 1)
                    match = re.match("^([^\.]+)\.([^\ ]+)\s+(.+)", line)
                    if match is None: continue
                    key   = match.group(1)
                    prop  = match.group(2)
                    value = match.group(3)
                    if not ret.get(key):
                        ret[key] = {}
                    ret[key][prop] = value
        return ret
