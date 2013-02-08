#!/usr/bin/make -f
# -*- makefile -*-

DESTDIR=
WEB_APP=usr/share/numeter/web-app
#HTTP_CONF=etc/nginx/sites-available

install:
	mkdir -p $(DESTDIR)/$(WEB_APP)
	cp -r web-app/src/* $(DESTDIR)/$(WEB_APP)
	#chown -R root:3 $(DESTDIR)/$(WEB_APP)
	#chown -R root:www-data $(DESTDIR)/$(WEB_APP)
	#install -d -m 0755 -o root -g root $(DESTDIR)/$(HTTP_CONF)
	#install	   -m 0755 -o root -g root web-app/numeter-web-app $(DESTDIR)/$(HTTP_CONF)

