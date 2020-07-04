import functools


@functools.singledispatch
def _parse(version):
    """Return a dict representation of the version."""
    if version is None:
        return {"major": 0, "minor": 1, "patch": 0}
    raise TypeError("Unsupported type")


@_parse.register(str)
def _from_str(version):
    atoms = list(map(int, version.split(".")))
    return _parse(atoms)


@_parse.register(list)
@_parse.register(tuple)
def _from_iter(version):
    if len(version) > 3:
        raise ValueError("semver only supports major, minor, patch versions")
    if len(version) == 0 or (len(version) == 1 and version[0] == 0):
        return {"major": 0, "minor": 1, "patch": 0}
    major = version[0]
    try:
        minor = version[1]
    except IndexError:
        minor = 0
    try:
        patch = version[2]
    except IndexError:
        patch = 0
    return {"major": major, "minor": minor, "patch": patch}


@_parse.register(int)
def _from_int(version):
    if version < 0:
        raise ValueError("Only non-negative integers allowed")
    return {"major": version, "minor": 0 if version else 1, "patch": 0}


@_parse.register(dict)
def _from_dict(version):
    filtered = {k: v for k, v in version.items() if k in ("major", "minor", "patch")}
    if "major" not in filtered:
        filtered["major"] = 0
    if "minor" not in filtered:
        filtered["minor"] = 0 if filtered["major"] else 1
    if "patch" not in filtered:
        filtered["patch"] = 0
    return filtered


@functools.total_ordering
class Version:
    def __init__(self, version=None):
        for attr, value in _parse(version).items():
            setattr(self, attr, value)

    def __repr__(self):
        return f"Version {self.major}.{self.minor}.{self.patch}"

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def _convert(cls, obj):
        """Convenience method to avoid lots of isinstance calls."""
        if isinstance(obj, cls):
            return obj
        return cls(obj)

    def _compare(self, other):
        try:
            other = self._convert(other)
        except (TypeError, ValueError):
            raise NotImplementedError()

        if self.major > other.major:
            return 1
        if self.major < other.major:
            return -1
        if self.minor > other.minor:
            return 1
        if self.minor < other.minor:
            return -1
        if self.patch > other.patch:
            return 1
        if self.patch < other.patch:
            return -1
        return 0

    def __lt__(self, other):
        return self._compare(other) == -1

    def __eq__(self, other):
        return self._compare(other) == 0

    def bump_major(self):
        return self.__class__({"major": self.major + 1, "minor": 0, "patch": 0})

    def bump_minor(self):
        return self.__class__(
            {"major": self.major, "minor": self.minor + 1, "patch": 0}
        )

    def bump_patch(self):
        return self.__class__(
            {"major": self.major, "minor": self.minor, "patch": self.patch + 1}
        )


def compare(version_a, version_b):
    version_a = Version._convert(version_a)
    return version_a._compare(version_b)


def max_version(versions):
    def bigger(version_a, version_b):
        return version_a if compare(version_a, version_b) >= 0 else version_b

    return Version._convert(functools.reduce(bigger, versions))


def min_version(versions):
    def smaller(version_a, version_b):
        return version_a if compare(version_a, version_b) < 0 else version_b

    return Version._convert(functools.reduce(smaller, versions))
