from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="plaster",
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
        "black==23.10.1",  # this should be the same with gdcdatamodel2's pre-commit-config file
        "click~=8.0",
        "dulwich",
        "isort==5.12.0",  # this should be the same with gdcdatamodel2's pre-commit-config file
        "Jinja2~=3.0",
        "jsonschema",
        "pyyaml==5.3.1",  #  https://github.com/yaml/pyyaml/issues/724
        "toml~=0.10",
        "psqlgml>=0.2.4",
        "psqlgraph~=3",
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
