#!/bin/bash

#foo_unittest|bar_unittest

echo '#!/bin/sh
# -*- sh -*-

if [ "$1" = "config" ]; then

	echo "graph_title foo_test"
	echo "graph_args --base 1000 -l 0 "
	echo "graph_vlabel foo vlabel"
	echo "foo.label foo label"
	echo "foo.draw AREA"
	exit 0
fi

echo "foo.value 42"
exit 0' >/etc/munin/plugins/foo_unittest



echo '#!/bin/sh
# -*- sh -*-

if [ "$1" = "config" ]; then

	echo "graph_title bar gnu test"
    echo "graph_order gnu bar"
	echo "graph_args --base 1024 -l 0 "
	echo "graph_vlabel bar vlabel"
	echo "bar.label bar label"
	echo "bar.draw LINE"
    echo "bar.type COUNTER"
	exit 0
fi

echo "bar.value -4.2"
echo "gnu.value 4.2"
exit 0' >/etc/munin/plugins/bar_unittest

chmod +x /etc/munin/plugins/bar_unittest
chmod +x /etc/munin/plugins/foo_unittest

/etc/init.d/munin-node restart >/dev/null 2>/dev/null
#sleep 1
#if [ -n $(echo -e 'fetch foo_unittestt\nquit\n' | nc 127.0.0.1 4949 | egrep -v '^(\.|#.*)$') ]; then exit 0; else exit 1; fi
#if [ -n "$(munin-run foo_unittestt | egrep -v '^(\.|#.*)$')" ]; then exit 0; else exit 1; fi
if [ -n "$(munin-run foo_unittest 2>&1 | egrep -v '^(\.|#.*)$')" ]; then echo -n "True"; else echo -n "False"; fi



