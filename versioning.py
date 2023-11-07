import re

from setuptools_scm import ScmVersion


def get_version(version: ScmVersion):
    if version.distance == 0:
        return str(version.tag)

    from setuptools_scm.version import guess_next_version

    branch = version.branch
    if branch.startswith("release"):
        format = "{guessed}.rc{distance}"
    elif branch.startswith("develop"):
        format = "{guessed}.a{distance}"
    else:
        local = re.sub("[^0-9a-zA-Z]+", ".", branch)
        format = f"{{guessed}}.dev{{distance}}+{local}"

    return version.format_next_version(guess_next_version, format)
