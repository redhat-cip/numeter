.. XXX: reference/datamodel and this have quite a few overlaps!

.. _overview:

############
Overview
############

.. image:: img/numeter_banner.png
    :align: center
    :width: 300px

The Numeter infrastructure : instances of every component may be added to handle the load 

All components can be installed on the same server or on multiple servers depending on their specifications.
For example, the Storage component is IO intensive while the Collector requires memory.
 
Numeter is written in Python and uses Redis. We are considering going from a pull mode to a push mode using rabbitmq.

***********
Components
***********

Current Numeter architecture :

.. image:: img/architecture.svg
    :width: 720px
    :height: 370px

**Poller :** An agent installed on the servers for which graphs are desired. It gathers data and keeps it in a Redis instance to allow asynchronous collection.

.. image:: img/poller.png

**Collector :** Data is fetched from the pollers and stored in a Redis instance until it is retrieved by the Storage component. 

.. image:: img/collector.png

**Storage :** Data is fetched from the collectors and then stored in RRD files. An HTTP API allows access to the data.

.. image:: img/storage.png

**Webapp :** A PHP webapp displays data using the dygraphs library

    * http://dygraphs.com/

.. image:: img/webapp.png

*********
Features
*********

  * Autoconfigure display with plugin datas
  * Get data from external sources like munin
  * No data loss in case of network failure
  * PNG graph export
  * User & Group management
  * Automatic dashboard creation
  * Open architecture allows new features to be created easily 
  * Scalable 



************************
Functional architecture
************************

Functional architecture :

.. image:: img/fonctional_architecture.svg
    :width: 100%
    :height: 380px


***********
Screenshot
***********


.. image:: img/screenshot/memory_graph.png
