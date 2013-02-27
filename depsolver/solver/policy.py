import collections

class Policy(object):
    """Policy classes implement a specific policy to deal with multiple
    solutions to the SAT problem (which version to select when multiple are
    available, etc...)."""
    def _compute_prefered_packages_installed_first(self, pool, installed_map, package_ids):
        """Returns a package name -> package queue mapping, with each queue
        being priority-sorted.

        It puts packages already installed first

        Arguments
        ---------
        pool: Pool
            Pool instance used to resolve packages, provides, etc...

        Returns
        -------
        package_queue: dict
            package name -> sorted queue of package ids. 
        """
        package_name_to_package_ids = collections.defaultdict(collections.deque)
        for package_id in package_ids:
            package = pool.package_by_id(package_id)
            if package_id in installed_map:
                package_name_to_package_ids[package.name].appendleft(package_id)
            else:
                package_name_to_package_ids[package.name].append(package_id)

        return package_name_to_package_ids

    def prefered_package(self, pool, installed_map, package_ids):
        # FIXME: this is more or less broken in most cases
        packages_by_priority = \
            self._compute_prefered_packages_installed_first(pool, installed_map,
                package_ids)
        packages = []
        for _packages in packages_by_priority.itervalues():
            packages.extend(_packages)

        return packages[0]
