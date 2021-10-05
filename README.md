[![Build Status](https://app.travis-ci.com/NCI-GDC/plaster.svg?token=5s3bZRahNJnkspYEMwZC&branch=master)](https://app.travis-ci.com/NCI-GDC/plaster)
# The Data Commons Model Source Generator Project (Plaster)
GDC internship project for generating data model source code.

# Goal
Generate source code that can replace the gdcdatamodel runtime generated code given any gdcdictionary.

This project is a reissue of the project https://github.com/NCI-GDC/gdcdatamodel, without challenges and obscurity associated with using gdcdatamodel. The resulting code will be readable, pass static and linting checks, completely remove delays from dictionary load times.

# Requirements

· Python >= 3.8

· No direct dependency on any dictionary versions

· Must expose scripts that can be invoked to generate source code

· Must include unit and integration tests with over 80% code coverage

· Must provide typings and pass mypy checks

