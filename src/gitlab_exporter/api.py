#!/usr/bin/env python
from . helpers import __version__
import argparse
import uuid
import pytz
import pprint
import gitlab 
import pypandoc as pc
from datetime import date, datetime, time, timedelta

# https://icalendar.readthedocs.io/en/latest/
from icalendar import Calendar, Event, vDatetime, vDate, Timezone

from . helpers.gldates2ics import Milestones2ics
from . helpers.issues2csv import Milestone, Issue, Issues2csv


def gmd(args):

    m2i = Milestones2ics(args)
    m2i.main()


def pmd(args):
    pass


def pi(args):

    i2c = Issues2csv(args)
    i2c.main()


def main():
    parser = argparse.ArgumentParser(prog="gitlab-exporter", description="Export various data sets from GitLab issues, projects and groups")
    parser.add_argument("gitlab_instance", help="URL of your GitLab instance, e.g. https://gitlab.com/")
    parser.add_argument("private_token", help="Access token for the API. You can generate one at Profile -> Settings")
    parser.add_argument("--version", action='version', help='Print the version of this program.', version='%(prog)s {}'.format(__version__))
    subparsers = parser.add_subparsers(help="Available subcommands")

    parser_gmd = subparsers.add_parser('gmd', help="Export dates from group milestones to an ICS calendar file.")
    parser_gmd.add_argument('group_id', type=int, help='The ID of a GitLab group with group milestones.')
    parser_gmd.add_argument("file_name", help="An individual file name for the ICS file. For security by obscurity, choose a hash-like one.")
    parser_gmd.add_argument("--cal-name", help="An individual name for the calendar. Shows up when subscribing to it. Default is 'GitLab Calendar'", default="GitLab Calendar")
    parser_gmd.add_argument("--no-extension", help="Use if your file name needs no file extension. Useful for online calendar subscriptions.", action="store_true")
    parser_gmd.add_argument("--with-issues", help="Use if you want to generate separate event for issues related to milestones", action="store_true")
    parser_gmd.add_argument("--time-zone", help="Default is 'Europe/Berlin'", default="Europe/Berlin")
    parser_gmd.set_defaults(func=gmd)

    parser_pmd = subparsers.add_parser('pmd', help="Export dates from project milestones to an ICS calendar file.")
    parser_pmd.add_argument('project_id', type=int, help='The ID of a GitLab project with milestones.')
    parser_pmd.set_defaults(func=pmd)

    parser_pi = subparsers.add_parser('pi', help="Export group issues to an CSV file.")
    parser_pi.add_argument('project_id', type=int, help='The ID of a GitLab project with issues.')
    parser_pi.add_argument("file_name", help="An individual file name for the ICS file. For security by obscurity, choose a hash-like one.")
    parser_pi.set_defaults(func=pi)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
