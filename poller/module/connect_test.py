#!/usr/bin/env python

import connect

c = connect.MuninConnection()

print c.munin_nodes()
print c.munin_list()
