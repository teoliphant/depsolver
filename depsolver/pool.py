import collections

from depsolver.errors \
    import \
        MissingPackageInPool
from depsolver.requirement \
    import \
        Requirement

MATCH_NAME = 1
MATCH = 2
MATCH_PROVIDE = 3

class Pool(object):
    """Pool objects model a pool of repositories.

    Pools are able to find packages that provide a given requirements (handling
    the provides concept from package metadata).
    """
    def __init__(self):
        self._id_to_package = {}

        # provide.name -> package.id mapping
        self._provide_name_to_ids = collections.defaultdict(list)

    def add_repository(self, repository):
        """Add a repository to this pool.

        Arguments
        ---------
        repository: Repository
            repository
        """
        for package in repository.iter_packages():
            self._id_to_package[package.id] = package

            self._provide_name_to_ids[package.name].append(package.id)
            for provide in package.provides:
                self._provide_name_to_ids[provide.name].append(package.id)

    def package_by_id(self, package_id):
        """Retrieve a package from its id.

        Arguments
        ---------
        package_id: str
            A package id
        """
        try:
            return self._id_to_package[package_id]
        except KeyError:
            raise MissingPackageInPool(package_id)

    def what_provides(self, requirement):
        """Returns a list of packages that provide the given requirement.

        Arguments
        ---------
        requirement: Requirement
            the requirement to match
        """
        # FIXME: this is conceptually copied from whatProvides in Composer, but
        # I don't understand why the policy of preferring non-provided over
        # provided packages is handled here.
        match_name = False
        matches = []
        provide_matches = []
        for candidate_id in self._provide_name_to_ids[requirement.name]:
            package = self._id_to_package[candidate_id]
            match = self.matches(package, requirement)
            if match == MATCH_NAME:
                match_name = True
            elif match == MATCH:
                match_name = True
                matches.append(package)
            elif match == MATCH_PROVIDE:
                provide_matches.append(package)

        if match_name:
            return matches
        else:
            return matches + provide_matches

    def matches(self, candidate, requirement):
        """Checks whether the candidate package matches the requirement, either
        directly or through provides.

        Arguments
        ---------
        candidate: Package
            Candidate package
        requirement: Requirement
            The requirement to match

        Returns
        -------
        match_type: _Match or False
            An instance of Match, that specified the type of match:
            
                - if only the name matches, will be MATCH_NAME
                - if the name and version actually match, will be MATCH
                - if the match is through the package's provides, will be MATCH_PROVIDE
                - if no match at all, will be False

        Examples
        --------
        >>> from depsolver.version import Version
        >>> from depsolver.requirement import Requirement
        >>> R = Requirement.from_string
        >>> V = Version.from_string
        >>> pool = Pool()
        >>> pool.matches(Package('numpy', V('1.3.0')), R('numpy >= 1.2.0'))
        MATCH
        """
        if requirement.name == candidate.name:
            candidate_requirement_string = "%s == %s" % (candidate.name, candidate.version)
            candidate_requirement = Requirement.from_string(candidate_requirement_string)
            if requirement.matches(candidate_requirement):
                return MATCH
            else:
                return MATCH_NAME

        for provide in candidate.provides:
            if requirement.matches(provide):
                return MATCH_PROVIDE

        return False
