import collections

from depsolver.errors \
    import \
        DepSolverError

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

    def prefered_package_ids(self, pool, installed_map, package_ids):
        """Return a list of preferred package ids to install for the given package
        ids list."""
        package_queues = \
            self._compute_prefered_packages_installed_first(pool, installed_map,
                package_ids)

        def package_id_to_version(package_id):
            package = pool.package_by_id(package_id)
            return package.version

        for package_name, package_queue in package_queues.iteritems():
            sorted_package_queue = sorted(package_queue, key=package_id_to_version)[::-1]
            package_queues[package_name] = sorted_package_queue

        for package_name, package_queue in package_queues.iteritems():
            package_queues[package_name] = prune_to_best_version(pool, package_queue)

        if len(package_queues) > 1:
            raise NotImplementedError("More than one package name in select " \
                                      "and install not supported yet")
        else:
            try:
                candidates = package_queues.itervalues().next()
            except StopIteration:
                raise DepSolverError("No candidate in package_queues ?")
            if len(candidates) > 1:
                raise NotImplementedError("More than one package in select " \
                                          "and install not supported yet")
            else:
                return candidates

def prune_to_best_version(pool, package_ids):
    # Assume package_ids is already sorted (from max to min)
    if len(package_ids) < 1:
        return []
    else:
        best_package = pool.package_by_id(package_ids[0])
        best_version_only = [package_ids[0]]
        for package_id in package_ids[1:]:
            package = pool.package_by_id(package_id)
            if package.version < best_package.version:
                break
            else:
                best_version_only.append(package_id)

        return best_version_only
