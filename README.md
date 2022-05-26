[![Build Status](https://app.travis-ci.com/NCI-GDC/plaster.svg?token=5s3bZRahNJnkspYEMwZC&branch=master)](https://app.travis-ci.com/NCI-GDC/plaster)

# The Data Commons Model Source Generator Project (Plaster)

GDC internship project for generating data model source code.

# Purpose

This project is a drop-in replacement to the project
https://github.com/NCI-GDC/gdcdatamodel,
without challenges and obscurity associated with using gdcdatamodel. The resulting code
will be readable, pass static and linting checks, completely remove delays from
dictionary load times.

# Goal

Given any compliant gdcdictionary, generate source code that can replace the
gdcdatamodel runtime generated code.

# Data Commons Models

The data commons are a collection of data structures representing concepts within a
subject area. These data structures usually form a graph with edges as relationships to one another. The data structures and relationships are defined as JSON schema in yaml files that are distributed via a git repository. These definitions are called Dictionaries for short. The gdcdictionary is one example of a data commons with a primarily focus on cancer. Dictionaries are updated and released frequently, with each release adding or removing nodes, edges, or properties.

# Associated Projects

- biodictionary: https://github.com/NCI-GDC/biodictionary
- gdcdatamodel: https://github.com/gdcdatamodel
- gdcdictionary: https://github.com/NCI-GDC/gdcdictionary
- psqlgml: https://github.com/NCI-GDC/psqlgml
- psqlgraph: https://github.com/NCI-GDC/psqlgraph

# Requirements

- Python >= 3.8
- No direct dependency on any dictionary versions
- Must expose scripts that can be invoked to generate source code
- Must include unit and integration tests with over 80% code coverage
- Must provide typings and pass mypy checks
