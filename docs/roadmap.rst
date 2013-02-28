.. XXX: reference/datamodel and this have quite a few overlaps!

.. _roadmap:

#######
Roadmap
#######

**Features roadmap :**
  * Webapp : Link a comment on a host for a timestamp
  * Webapp : Override graph template
  * Webapp : REST api to manage hosts / users datas and get it in JSON format
  * Poller : OpenStack polling like Ceilometer

**Architecture roadmap :**
  * Customize fetch time for a plugin
  * Use a different storage for datas (like carbon or mongodb)
  * Change poller pull tu push (with rabbitmq for example)
  * Use sqlite in poller insted of redis
  * Whisper / carbon support
  * Push mode for pollers with RabbitMQ
  * Different precision per Plugin
  * Poller : SQLlite support or directly store a file in RAM
  * Split datas from configuration (which able to push RAW datas without configuration)
