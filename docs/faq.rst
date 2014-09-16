.. _faq:

############
FAQ
############

**How to build the sphinx doc ?** : The api.rst use doc strings and need to import Numeter modules. So the doc is builded by tox. ::

  tox -e docs

**How to launch unit tests ?** : Launch unit tests with tox ::

  tox -epy27 tests/units



