#!/usr/bin/make -f
# -*- makefile -*-

DESTDIR=
PLUGINS_DIR=usr/share/munin-numeter/plugins

install:
	mkdir -p $(DESTDIR)/$(PLUGINS_DIR)
	cp -r munin-plugins/plugins/* $(DESTDIR)/$(PLUGINS_DIR)
	#chown -R root:3 $(DESTDIR)/$(WEB_APP)
	#chown -R root:www-data $(DESTDIR)/$(WEB_APP)
	#install -d -m 0755 -o root -g root $(destdir)/$(http_conf)
	#install	   -m 0755 -o root -g root web-app/numeter-web-app $(destdir)/$(http_conf)

