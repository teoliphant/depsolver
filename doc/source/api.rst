.. _api:

API
===

.. module:: depsolver

This part of the documentation covers all the interfaces of depsolver.

Pool object
-----------

.. currentmodule:: depsolver.pool

.. autoclass:: Pool
   :members:

Repository object
-----------------

.. currentmodule:: depsolver.repository

.. autoclass:: Repository
   :members:

Requirement-related functionalities
-----------------------------------

.. currentmodule:: depsolver.requirement

.. autoclass:: Requirement
   :members:

Version-related functionalities
-------------------------------

This modules contains a Version class + a few utilities that allows to compare
versions in a consistent way.

.. currentmodule:: depsolver.version

.. autofunction:: is_version_valid

.. autoclass:: Version
   :members:

.. autoclass:: MinVersion

.. autoclass:: MaxVersion
