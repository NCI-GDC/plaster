import os
import re
from os import path

from setuptools import find_packages, setup
from setuptools_scm import Configuration
from setuptools_scm._get_version_impl import parse_version

current_dir = path.abspath(path.dirname(__file__))

with open(path.join(current_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


def get_version():
    config = Configuration()
    version = parse_version(config)
    if version.distance == 0:
        return str(version.tag)

    from setuptools_scm.version import guess_next_version

    branch = os.getenv("CI_COMMIT_REF_NAME", version.branch)
    if branch.startswith("release"):
        fmt = "{guessed}rc{distance}"
    elif branch.startswith("develop"):
        fmt = "{guessed}a{distance}"
    else:
        local = re.sub("[^0-9a-zA-Z]+", ".", branch)
        fmt = f"{{guessed}}.dev{{distance}}+{local}"

    return version.format_next_version(guess_next_version, fmt)


setup(
    name="gdc-plaster",
    author="Rowland Ogwara",
    author_email="rogwara@uchicago.edu",
    keywords="GDC,datamodels,generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache 2.0",
    url="https://github.com/NCI-GDC/plaster",
    description="GDC data models generator",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    zip_safe=True,
    include_package_data=True,
    python_requires=">=3.8",
    setuptools_git_versioning={
        "enabled": True,
        "version_callback": get_version,
    },
    classifiers=[
        "Development Status :: 2 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    install_requires=[
        "click~=8.0",
        "dulwich",
        "Jinja2~=3.0",
        "jsonschema",
        "pyyaml>=6.0.1",  #  https://github.com/yaml/pyyaml/issues/724
        "toml~=0.10",
        "psqlgml>=0.2.4",
        "psqlgraph>=3",
    ],
    extras_require={
        "dev": [
            "coverage[toml]~=5.5",
            "deepdiff~=5.8.1",
            "mypy==0.910",
            "pre-commit~=2.13",
            "pytest~=6.2",
            "pytest-cov~=2.12",
            "pytest-psqlgraph~=0.1",
        ],
        "docs": [
            "sphinx~=4.1",
            "sphinx_rtd_theme~=0.5",
            "sphinxcontrib-napoleon~=0.7",
        ],
        "examples": [
            "pytest~=6.2",
            "pytest-psqlgraph>=0.1.1",
        ],
    },
    entry_points={"console_scripts": ["plaster=plaster.cli:app"]},
)
