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

Requirement objects represent a name + a set of constraints that have to be
match for that requirement to be considered fulfilled.

Typically, it will be a version constraint, e.g. 'numpy >= 1.6.0'.

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
