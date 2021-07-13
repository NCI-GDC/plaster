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
    setup_requires=["setuptools_scm"],
    classifiers=[
        "Development Status :: 2 - Alpha",
        "Intended Audience :: PSQLGrpah Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=[
        "click~=8.0",
        "Jinja2~=3.0",
        "PyYaml~=5.4",
        "toml~=0.10",
    ],
    extras_require={
        "dev": [
            "black==21.6b0",
            "coverage[toml]~=5.5",
            "flake8~=3.9",
            "mypy==0.910",
            "pre-commit~=2.13",
            "pytest~=6.2",
            "pytest-cov~=2.12",
            "sphinx~=4.1",
            "sphinx_rtd_theme~=0.5",
            "sphinxcontrib-napoleon~=0.7",
        ]
    },
    entry_points={"console_scripts": ["plaster=plaster.cli:app"]},
)
