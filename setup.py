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
    python_requires=">=3.9",
    setup_requires=["setuptools_scm"],
    install_requires=[
        "click",
        "Jinja2",
    ],
    extras_require={
        "dev": [
            "black",
            "coverage[toml]",
            "flake8",
            "mypy",
            "pre-commit",
            "pytest",
            "pytest-cov",
            "pytest-flask",
            "sphinx",
            "sphinx_rtd_theme",
            "sphinxcontrib-napoleon",
        ]
    },
)
