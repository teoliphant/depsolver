Welcome to depsolver
====================

Welcome to Depsolver's documentation.

Depsolver is a library for package dependency management in python. While it is
intended to be used in Bento, it is completely independent of it, and should be
usable for other packaging methods (even ones not in Python).

Its intended features are:

        - handle install, removal, update and upgrade
        - handle dependencies (not just runtimes, but also build, test, etc...
          dependencies)
        - handle the notions of provides, obsoletes, conflicts
        - ability to easily mix and match multiple repositories
        - allow for different policies for upgrade/update

As of today (Feb 2013), it is very experimental and not recommended for production usage.

.. include:: contents.rst.inc
