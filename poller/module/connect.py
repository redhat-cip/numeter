#!/usr/bin/env python

import socket
import re

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
        with MuninSock() as self.sock:
	    self._s = self.sock.makefile()
            self.sock.sendall("fetch %s\n" % key)
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
        with MuninSock() as self.sock:
            self._s = self.sock.makefile()
            self.sock.sendall("list %s\n" % node)
            return_list = self._readline().split(' ')
        return return_list if return_list != [''] else []

    def munin_nodes(self):
        with MuninSock() as self.sock:
            self._s = self.sock.makefile()
            self.sock.sendall("nodes\n")
            return_node = [ line for line in self._iterline() ]
        return return_node[0] if return_node else None


    def munin_config(self, key):
        with MuninSock() as self.sock:
            self._s = self.sock.makefile()
            self.sock.sendall("config %s\n" % key)
            ret = {}
            for line in self._iterline():
                if line.startswith('graph_'):
                    try:
                        key, value = line.split(' ', 1)
                        ret[key] = value
                    except ValueError:
                        self._logger.info("myMuninModule : skipped key " + key)
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
        # Close munin connexion to avoid fucked plugin
        return ret

