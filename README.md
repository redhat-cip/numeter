# Numeter
Numeter is a new graphing solution (i.e. Cacti) made by some
guys working at eNovance. The three components Poller, collector and storage are written in Python with datas which are
stored in a Redis DB and written to disk in RRD files. The webapp is written in PHP.

Documentation is available here: https://numeter.readthedocs.org

**Features :**
* Graphs with dygraphs and highcharts
* User and group management
* Use graph template configuration give by poller
* Already works with munin-node
* Poller Keep datas in cache in case of network failure
* Scalable architecture

**Roadmap :**
* API : Manage Users
* API : Read Datas in JSON
* Attach comments on graphs
* Connection with OpenStack / Ceilometer
* Whisper / carbon support
* Push mode for pollers with RabbitMQ
* Different precision per Plugin
* Poller : SQLlite support or directly store a file in RAM
* Split datas from configuration (which able to push RAW datas without configuration)


License : AGPLv3
