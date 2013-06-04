.. XXX: reference/datamodel and this have quite a few overlaps!

.. _about:

############
About
############

Like many, we started with Cacti and Munin a long time ago. Then, we joined these two software packages into one and we called it Mucti.

Over time and with an increasing number of hosts, we have seen the limitations of this approach. 
We launched the Numeter project, aiming for more modularity and scalability.

Each component of the Numeter architecture can be installed separately.
Our policy for the project is to rely on standard technologies and therefore JSON is used for communication between the components and to access data using the HTTP API

You are free to use only the components you need. 
For example, the poller with your modules or develop your own application to process the data contained in the storage component.
