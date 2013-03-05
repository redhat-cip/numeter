.. XXX: reference/datamodel and this have quite a few overlaps!

.. _overview:

############
Overview
############

Infrastructure Numeter : le but est de pouvoir ajouter chaque êlement X fois selon le besoin.

Chaque élément peut être installé sur la même machine ou des machines différentes suivant leurs caractéristiques.
Par exemple le Storage a besoin d'IO alors que le collector de RAM. 

Numeter est écrit en Python et utilise redis. Nous faisons actuellement le choix pour passer d'un poller mode pull en mode push avec par exemple rabbitmq.

.. image:: img/numeter_banner.png
    :align: center
    :width: 300px

***********
Components
***********

Actual Numeter architecture :

.. image:: img/architecture.svg
    :width: 720px
    :height: 370px

La webapp est en php et fonctionne avec :

    * http://www.highcharts.com/
    * http://dygraphs.com/

*********
Features
*********

  * Autoconfigure display with plugin datas
  * Get datas from external sources like munin
  * Keep data if network fail between poller and collector
  * Graphs export des graphs en PNG, ...
  * Gestion des utilisateurs et groupes
  * Auto création de dashboard
  * Implémentation de features facilement (architecture ouverte)
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
