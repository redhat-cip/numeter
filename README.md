# Numeter
Numeter is a new graphing solution (like Cacti for example) made by some
guys working at eNovance. Poller, collector and storage are written in Python and datas are
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
* Api pour ajouter des utilisateurs / ...
* Api pour lire les datas en json
* Accrocher des commentaires sur des graphs
* Connexion à openstack / ceilometer.
* Utilisation de whisper / carbon
* Mode push pour les pollers avec rabbitmq
* Précision différente par plugin
* Utilisation de sqlite ou objet en ram sur la partie poller
* Découpler les datas des config (possibilité de push des datas brute sans config)
