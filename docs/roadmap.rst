.. XXX: reference/datamodel and this have quite a few overlaps!

.. _roadmap:

#######
Roadmap
#######


**roadmap :**
  * Keep in mind the idea is to write independent blocks that can be used separately
  * Change poller pull tu push with rabbitmq or twisted for example (Need to design and test solutions) ?
     * rabbitmq allow you to have 2 product : poller get datas from munin, ... and push them in a queue. And storage, Just read datas form a queue.
  * Daemonize Numeter. Remove scripts in cron
  * Poller : SQLlite support or directly store a file in RAM
  * Storage : Use a different storage for datas (like carbon or mongodb)
  * Hosts management :
     * Who resolve a duplicate host
     * Who add new host and dynamicaly choose the collector or storage
  * poller : Make poller module or break the poller to allow Split datas from configuration (which able to push RAW datas without configuration like carbon)
  * poller : Different precision per Plugin
  * webapp : Rebuild or not the webapp in Django ?
  * Poller : add threads for modules and myMuninModule
  * Webapp : Link a comment on a host for a timestamp
  * Webapp : Override graph template
  * Webapp : REST api to manage hosts / users datas and get it in JSON format
  * Poller : OpenStack poller module get datas from Ceilometer, ...
