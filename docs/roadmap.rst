.. XXX: reference/datamodel and this have quite a few overlaps!

.. _roadmap:

#######
Roadmap
#######

**Features roadmap :**
  * Webapp : Link a comment on a host for a timestamp
  * Webapp : Override graph template
  * Webapp : Rest api to add host / users / get datas in json format
  * Poller : OpenStack polling like ceilometer

**Architecture roadmap :**
  * Customize fetch time for a plugin
  * Use a different storage for datas (like carbon or mongodb)
  * Change poller pull tu push (with rabbitmq for exemple)
  * Use sqlite in poller insted of redis
