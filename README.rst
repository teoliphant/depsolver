This is a prototype for a decent dependency solver for python.

Its requirements are the following:

        - version based on `semantic versions RFC <http://www.semver.org>`_ (version
          2.0.0-rc1 at this time)
        - handles dependency in a sane way
        - pluggable back-end for metadata storage
        - reasonable fast: resolving dependencies should not take too long (not
          more than a few seconds for a user who has only a few tens of
          packages currently installed)
        - well tested and documented

The design is strongly inspired from `PHP Composer packager
<http://getcomposer.org>`_, itself started as a port of libsolver.
