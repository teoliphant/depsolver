.. image:: https://secure.travis-ci.org/enthought/depsolver.png
    :alt: Travis CI Build Status

This is a prototype for a decent dependency solver for python.

Example::

    # Install numpy
    numpy_1_6_1 = Package.from_string("numpy-1.6.1")
    numpy_1_7_0 = Package.from_string("numpy-1.7.0")

    repo = Repository([numpy_1_6_1, numpy_1_7_0])

    pool = Pool()
    pool.add_repository(repo)

    installed_repo = Repository()

    # only one operation here: install numpy 1.7.0
    operations = solve(pool, req, installed_repo, Policy())

More complex scenarios are also supported, e.g.:

    - direct dependencies, obviously (if A depends on B, B is installed first)
    - packages can provide other packages
    - does not update already installed packages if they satisfy the requirements

Many more are not yet supported:

    - declaring conflicts and obsoletes
    - real policies that can be customized
    - support for update
    - version pinning
    - repositories that are not in-memory (e.g. remote ones)

Depsolver main planned features are:

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

Thanks to Enthought to let me open source this project !
