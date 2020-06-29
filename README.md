# gitlab-exporter

Python tool for the command line to export various data sets from GitLab like project issues and group milestone dates. Scales nicely due to an API built on submodules.

*gitlab-exporter* is based on [argparse](https://docs.python.org/3.7/library/argparse.html#module-argparse) and uses [python-gitlab](https://python-gitlab.readthedocs.io/en/stable/) under the hood.

## Motivation

At TUHH we use GitLab CE a lot for project management. The Community Edition (CE) is missing some features that premium versions of GitLab have. As we want to stay independent with MIT licensed distribution of GitLab we have to implement the missing features ourselves.

It takes some time and patience to get all colleagues into working with GitLab. For many of them GitLab is not the tool that they open up first when they start working. Thus, some workarounds and helper functions can make their work more convenient and fun, as not all of them are coders.

*gitlab-exporter* is such a helper tool. Its purpose is to get data out off GitLab and locate it in your colleagues' personal digital environments like calendars, office programs and the like.

## Installation

### Requirements

You need at least on your system

- Python 3.6.x
- pandoc 2.x

### Installation from Source

Go to [the repository](https://collaborating.tuhh.de/hos/modernes-publizieren/offen/software/middleware/gitlab-exporter) and grab the source.

### Installation using Pip

*gitlab-exporter* is a Python tool that can easily be installed with pip.

    pip install gitlab-exporter

After installation with pip you should be able to use the command `gitlab-exporter` in your shell.

## Getting to know the API

To learn about the API of *gitlab-exporter* type

    gitlab-exporter -h

after installation. There are and will be several submodules for different purposes. Learn about the API of these submodules simply typing e.g.

    gitlab-exporter gmd -h

to get help for the submodule that exports group milestone dates to an ICS file.

## Submodules and Examples

*gitlab-exporter* provides several submodules for different purposes.

### `gmd` - group milestone dates

Exports dates and descriptions of milestones on the group level to an ICS file. You then can import this file into your calendar of choice.

Example:

    gitlab-exporter https://my-gitlab.com A2DF6HE6R7C88C9AE gmd 1234 milestones.ics

The command consists of the GitLab instance, a private token, the submodule name, the group id and the file name of the ICS file.

### `pi` - project issues

Exports issues belonging to a certain project to a CSV file.

    gitlab-exporter https://my-gitlab.com A2DF6HE6R7C88C9AE pi 2345 issues.csv

The command consists of the GitLab instance, a private token, the submodule name, the project id and the CSV file name.

## Automate the boring stuff with Docker

If you have the CI/CD component running with GitLab you can easily have Docker build your exports from GitLab.

Further documentation is on the way...

## Tests

There are some, but they will be updated to [pytest](https://docs.pytest.org/en/latest/index.html) as soon as possible.

## License

Copyright 2019 Axel Dürkop; Hamburg University of Technology (TUHH)

This piece of software is licensed under the [**Apache License, Version 2.0**](https://collaborating.tuhh.de/hos/modernes-publizieren/offen/software/middleware/gitlab-exporter/blob/master/LICENSE)