<img src="https://raw.githubusercontent.com/enovance/numeter/master/docs/img/numeter_banner.png" width='500px'>

[![Build Status](https://travis-ci.org/enovance/numeter.svg?branch=master)](https://travis-ci.org/enovance/numeter)

Numeter is a new and dynamic graphing solution made by some of the 
folks at eNovance. We use it as part of our cloud solutions. It is 
based on Python, sexy and highly scalable.

**Documentation :** https://numeter.readthedocs.org

**Features :**
* Graphs with dygraphs
* User and group management
* Use graph template configuration give by poller
* Already works with munin-node
* Poller Keep datas in cache in case of network failure
* Scalable architecture

**How to get started :**
* Visit the Official Website : http://enovance.github.com/numeter/

**License : AGPLv3**


**Quick overview :**
* The Numeter infrastructure : instances of every component may be added to handle the load.
* All components can be installed on the same server or on multiple servers depending on their specifications.
* Numeter is written in Python and uses Redis. We are considering going from a pull mode to a push mode using rabbitmq.

Current Numeter architecture :
<img src="https://raw.githubusercontent.com/enovance/numeter/master/docs/img/architecture.png" width='600px'>

* **Poller :** An agent installed on the servers for which graphs are desired. It gathers data and send them to an rpc. In case of network failure all datas are preserved and sent when network is back.
* **Rpc :** Receive data from poller and provide them to storage.
* **Storage :** Data is fetched from the rpc and then stored in WSP files. An HTTP API allows access to the data.
* **Webapp :** A Django webapp displays data using the js library like dygraphs

**Screenshots :**

<img src="https://raw.githubusercontent.com/enovance/numeter/master/docs/img/screenshot/memory_graph.png" width='600px'>
