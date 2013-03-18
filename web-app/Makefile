#!/usr/bin/make -f
# -*- makefile -*-

DESTDIR=
WEB_APP=usr/share/numeter/web-app
#HTTP_CONF=etc/nginx/sites-available

install:
	mkdir -p $(DESTDIR)/$(WEB_APP)
	cp -r web-app/src/* $(DESTDIR)/$(WEB_APP)
	if [ $(shell id -g www-data) ];\
	then\
	    chown -R root:www-data $(DESTDIR)/$(WEB_APP)/app/tmp/cache/;\
	    chmod -R g+w $(DESTDIR)/$(WEB_APP)/app/tmp/cache/;\
	fi
	#install -d -m 0755 -o root -g root $(DESTDIR)/$(HTTP_CONF)
	#install	   -m 0755 -o root -g root web-app/numeter-web-app $(DESTDIR)/$(HTTP_CONF)

