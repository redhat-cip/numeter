.. XXX: reference/datamodel and this have quite a few overlaps!

.. _about:

############
About
############

Au départ, comme beaucoup nous avons commencé il y a longtemps sur
cacti / munin. Nous avons réuni ces deux produits pour en faire un : Mucti.

Avec le temps et le nombre de hosts augmentant, nous avons vite vu les limites.
Nous avons alors lancé le projet Numeter avec pour but d'être plus scalable et modulaire pour
permettre de s'interfacer avec chaque élément facilement. 

L'architecture actuelle de numeter permet d'installer chaque élément séparément et garde comme
politique d'utiliser des technologies standard comme par exemple le format JSON pour les données
entre le poller, collector, storage, webapp. Ou l'accessibilité des données des storages par une
API HTTP servant du JSON.

Libre à vous d'utiliser uniquement le poller avec vos modules ou de développer votre propre application
pour traiter les données du storage.
