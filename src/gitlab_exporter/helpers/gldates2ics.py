#!/home/duerkop/.virtualenvs/gitlab/bin/python3

import uuid
import pytz
import pprint
import argparse
import gitlab 
import pypandoc as pc
from datetime import date, datetime, time, timedelta

# https://icalendar.readthedocs.io/en/latest/
from icalendar import Calendar, Event, vDatetime, vDate, Timezone

class Milestones2ics:

    def __init__(self, args):
        self.gitlab_instance = args.gitlab_instance
        self.private_token = args.private_token
        self.group_id = args.group_id
        self.file_name = args.file_name
        self.cal_name = args.cal_name
        self.with_issues = args.with_issues
        self.tz = pytz.timezone(args.time_zone) 

        try:
            self.gl = gitlab.Gitlab(
                self.gitlab_instance,
                private_token = self.private_token)
        except gitlab.config.GitlabConfigMissingError as err:
            print(err)


    def convert_timestamp_for_ical(self, timestamp):
        time_stamp = datetime.strptime(timestamp, "%Y-%m-%d")
        time_stamp_loc = self.tz.localize(time_stamp, is_dst=False)
        # print(self.tz)
        # print(time_stamp_loc)
        return time_stamp_loc

    def convert_timestamp_for_ical_with_time(self, timestamp):
        time_stamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        time_stamp_loc = self.tz.localize(time_stamp, is_dst=False)
        # print(time_stamp_loc)
        return time_stamp_loc
        

    def make_readable(self, cal):
        """Generate a human-readable version of calendar."""
        return cal.to_ical().decode("utf-8").replace("\r\n", "\n").strip()

    def fetch_projects(self):
        projects = self.gl.projects.list()
        return projects


    def fetch_groups(self):
        groups = self.gl.groups.list()
        # print(groups)
        return groups

    
    def fetch_group(self, group_id):
        try:
            group = self.gl.groups.get(group_id)
            # print(type(group))
            return group
        except gitlab.exceptions.GitlabGetError as err:
            print(err)


    def fetch_group_milestones(self, group):
        milestones = group.milestones.list(all=True)
        # print(milestones)
        return milestones


    def fetch_milestone_data(self, group, milestone):

        milestone_data = group.milestones.get(milestone.id)
        # print(milestone_data)
        return milestone_data


    def get_milestone_title(self, milestone):
        title = milestone.attributes["title"]
        # print(title)
        return title


    def get_milestone_description(self, milestone, convert=True):
        description = milestone.attributes["description"]

        if convert:
            description = pc.convert_text(description, "md", format="md")
            # print(description)
            # @TODO
            # description = ""
            return description
        else:
            # @TODO
            # description = ""
            return description


    def get_milestone_start_date(self, milestone):
        start_date = milestone.attributes["start_date"]
        # print(start_date)
        return start_date


    def get_milestone_due_date(self, milestone):
        due_date = milestone.attributes["due_date"]
        # print(due_date)
        return due_date


    def get_milestone_created_date(self, milestone):
        created_date = milestone.attributes["created_at"]
        # print(created_date)
        return created_date

    
    def get_milestone_updated_date(self, milestone):
        updated_date = milestone.attributes["updated_at"]
        # print(updated_date)
        return updated_date


    def get_milestone_state(self, milestone):
        state = milestone.attributes["state"]
        # print(state)
        return state


    def get_milestone_web_url(self, milestone):
        web_url = milestone.attributes["web_url"]
        # print(web_url)
        return web_url


    ##### Getter for issues

    def get_issue_title(self, issue):
        title = issue.attributes["title"]
        # print(title)
        return title


    def get_issue_description(self, issue, convert=True):
        description = issue.attributes["description"]

        if convert:
            description = pc.convert_text(description, "md", format="md")
            # print(description)
            # @TODO
            # description = ""
            return description
        else:
            # @TODO
            # description = ""
            return description


    def get_issue_start_date(self, issue):
        # due_date is correct here!
        start_date = issue.attributes["milestone"]["due_date"]
        # print(due_date)
        return start_date


    def get_issue_due_date(self, issue):
        due_date = issue.attributes["milestone"]["due_date"]
        # print(due_date)
        return due_date


    def get_issue_created_date(self, issue):
        created_date = issue.attributes["created_at"]
        # print(created_date)
        return created_date


    def get_issue_updated_date(self, issue):
        updated_date = issue.attributes["updated_at"]
        # print(created_date)
        return updated_date


    def get_issue_web_url(self, issue):
        web_url = issue.attributes["web_url"]
        # print(web_url)
        return web_url


    def count_related_issues(self, milestone):
        return len(milestone.issues().manager.list(milestone=milestone.title, state="opened"))

    def get_related_issues(self, milestone):
        return milestone.issues().manager.list(milestone=milestone.title, state="opened")


    def build_related_issues_list(self, milestone):
        issues_textlist = ""
        related_issues = milestone.issues().manager.list(milestone=milestone.title, state="opened")
        if self.count_related_issues(milestone) > 0:
            issues_textlist = "\n\nIssues\n------\n"
            for i in related_issues:
                issues_textlist = issues_textlist + "- {title}: {web_url}\n".format(title=i.title, web_url=i.web_url)
        return issues_textlist

    
    def extract_data_from_issue(self, milestone):
        for issue in self.get_related_issues(milestone):
            event_data = {}

            event_data["title"] = self.get_issue_title(issue)
            event_data["description"] = self.get_issue_description(issue)
            if self.get_issue_start_date(issue) is not None:
                event_data["start_date"] = self.convert_timestamp_for_ical(self.get_issue_start_date(issue)).date()
            if self.get_issue_due_date(issue) is not None:
                event_data["due_date"] = self.convert_timestamp_for_ical(self.get_issue_due_date(issue)).date()
            event_data["web_url"] = self.get_issue_web_url(issue)
            event_data["created_date"] = self.convert_timestamp_for_ical_with_time(self.get_issue_created_date(issue))
            # @TODO Implement this!
            event_data["updated_date"] = self.convert_timestamp_for_ical_with_time(self.get_issue_updated_date(issue))
            
            event = self.build_icalendar_event(event_data)
            self.cal.add_component(event)


    def extract_data_from_milestones(self, group, milestones):
        for milestone in milestones:
            milestone = self.fetch_milestone_data(group, milestone)

            event_data = {}

            event_data["title"] = self.get_milestone_title(milestone)
            if self.get_milestone_start_date(milestone) is not None:
                event_data["start_date"] = self.convert_timestamp_for_ical(self.get_milestone_start_date(milestone)).date()
            if self.get_milestone_due_date(milestone) is not None:
                event_data["due_date"] = self.convert_timestamp_for_ical(self.get_milestone_due_date(milestone)).date() + timedelta(days=1)
            event_data["created_date"] = self.convert_timestamp_for_ical_with_time(self.get_milestone_created_date(milestone))
            event_data["updated_date"] = self.convert_timestamp_for_ical_with_time(self.get_milestone_updated_date(milestone))
            event_data["web_url"] = self.get_milestone_web_url(milestone)
            event_data["state"] = self.get_milestone_state(milestone)

            event_data["description"] = "{description}{issues}".format(
                description=self.get_milestone_description(milestone, convert=True),
                issues = self.build_related_issues_list(milestone))

            # Add related issues to description
            event = self.build_icalendar_event(event_data)
            self.cal.add_component(event)

            # Generate separate events for calendar if --with-issues is set
            if self.with_issues:
                if self.count_related_issues(milestone) > 0:
                    self.extract_data_from_issue(milestone)




    def build_icalendar_event(self, event_data):
        event = Event()
        start_date = False
        due_date = False

        event["summary"] = event_data["title"]
        # Check if a start date exists. If not make the start_date
        # the due_date
        if "start_date" in event_data:
            # event["dtstart"] = vDate(event_data["start_date"]).to_ical()
            event.add('dtstart', event_data["start_date"])
            start_date = True
        if "due_date" in event_data:
            # event["dtend"] = vDate(event_data["due_date"]).to_ical()
            event.add('dtend', event_data["due_date"])
            due_date = True
        if due_date and not start_date:
            # event["dtstart"] = vDate(event_data["due_date"]).to_ical()
            event.add('dtstart', event_data["due_date"])
        event["description"] = event_data["description"]
        event["location"] = event_data["web_url"]
        event['created'] =  vDatetime(event_data["created_date"]).to_ical()
        event['last-modified'] =  vDatetime(event_data["updated_date"]).to_ical()
        event['dtstamp'] = vDatetime(datetime.now(tz=self.tz)).to_ical()
        event['uid'] = str(uuid.uuid1())

        # print(event.to_ical().splitlines())

        return event


    def build_cal_preamble(self):
        self.cal.add("prodid", "//Mozilla.org/NONSGML Mozilla Calendar V1.1//EN")
        self.cal.add("version", "2.0")
        self.cal.add("x-wr-timezone", "Europe/Berlin")
        self.cal.add("x-wr-calname", self.cal_name)
        self.cal.add("calscale", "Gregorian")


    def write_cal_to_disk(self):
        with open(self.file_name, "wb") as f:
            # f.write(self.make_readable(self.cal))
            f.write(self.cal.to_ical())


    # -- Hauptprogramm --

    def main(self):
        """Mainprogram: Generates an ICS file."""

        self.fetch_projects()
        self.fetch_groups()
        group = self.fetch_group(self.group_id)
        milestones = self.fetch_group_milestones(group)

        if len(milestones) > 0:

            self.cal = Calendar()
            self.build_cal_preamble()
            self.extract_data_from_milestones(group, milestones)

            try:
                self.write_cal_to_disk()
                # print(self.make_readable(self.cal))
            except IOError as err:
                print(err)

        else:
            print("No milestones for this group!")


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(prog="gldates2ics", description="Generate an calendar file from GitLab milestones following ICS standards.")
#     parser.add_argument("gitlab_instance", help="URL of your GitLab instance, e.g. https://gitlab.com/")
#     parser.add_argument("private_token", help="Access token for the API. You can generate one at Profile -> Settings")
#     parser.add_argument("group_id", help="The ID of a GitLab group with group milestones", type=int)
#     parser.add_argument("file_name", help="An individual file name for the ICS file. For security by obscurity, choose a hash-like one.")
#     parser.add_argument("--cal-name", help="An individual name for the calendar. Shows up when subscribing to it. Default is 'GitLab Calendar'", default="GitLab Calendar")
#     parser.add_argument("--no-extension", help="Use if your file name needs no file extension. Useful for online calendar subscriptions.", action="store_true")
#     parser.add_argument("--with-issues", help="Use if you want to generate separate event for issues related to milestones", action="store_true")
#     parser.add_argument("--time-zone", help="Default is 'Europe/Berlin'", default="Europe/Berlin")
#     args = parser.parse_args()

#     m2i = Milestones2ics(args)
#     m2i.main()