#!/home/duerkop/.virtualenvs/gitlab/bin/python3

#import pypandoc as pc
import os
import re
import gitlab
import pandas as pd
from datetime import date, datetime, time, timedelta
import argparse
from tqdm import tqdm
from pandas import ExcelWriter
import urllib.request
import shutil

class Milestone:

    def __init__(self, milestone):
        self.iid = milestone['iid']
        self.title = milestone['title']

    
    def __str__(self):
        return self.title


    def to_dict(self):
        return  { self.iid:
            {
                "Title": self.title
            }
        }

MARKDOWN_INLINE_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

class Issue:

    def __init__(self, issue):
        #print(issue.attributes)
        self.id = issue.attributes['id']
        self.iid = issue.attributes['iid']
        self.title = issue.attributes['title']
        self.description = issue.attributes['description'] or ""
        self.state = issue.attributes['state']
        self.created_at = issue.attributes['created_at']
        self.updated_at = issue.attributes['updated_at']
        if 'closed_at' in issue.attributes:
            self.closed_at = issue.attributes['closed_at']
        else:
            self.closed_at = None
        if 'closed_by' in issue.attributes:
            self.closed_by = issue.attributes['closed_by']
        else:
            self.closed_by = None
        self.labels = issue.attributes['labels']
        self.milestone = issue.attributes['milestone']
        self.assignees = issue.attributes['assignees']
        self.author = issue.attributes['author']
        self.user_notes_count = issue.attributes['user_notes_count']
        self.due_date = issue.attributes['due_date']
        self.web_url = issue.attributes['web_url']


    def __str__(self):
        return self.title

    
    def to_dict(self):

        milestone = ""

        if self.milestone is not None:
            milestone = Milestone(self.milestone)
        # https://docs.gitlab.com/ee/api/issues.html
        return { 
                "Id": self.id,
                "Type": "Issue",
                "Iid": self.iid,
                "Title": self.title,
                "Description": self.description, #pc.convert_text(self.description, "plain", format="md").strip(),
                "Status": self.state,
                "Due Date": self.due_date,
                "Labels": ','.join(self.labels),
                "Milestone": milestone,
                "Assignees": ','.join([a['name'] for a in self.assignees]),
                "Author": self.author['name'],
                "User Notes Count": self.user_notes_count,
                "URL": self.web_url,
                "Created": self.created_at,
                "Updated": self.updated_at
                }
    
    def get_links(self):
        links = dict(MARKDOWN_INLINE_LINK_RE.findall(self.description))
        return links
    
    def get_baseurl(self):
        return self.web_url.replace("/issues/" + str(self.iid), "")

class Note:

    def __init__(self, note):
        #print(issue.attributes)
        self.id = note.attributes['id']
        self.body = note.attributes['body']
        self.attachment = note.attributes['attachment']
        self.author = note.attributes['author']
        self.created_at = note.attributes['created_at']
        self.updated_at = note.attributes['updated_at']
        self.system = note.attributes['system']


    def __str__(self):
        return self.id

    
    def to_dict(self):
        # https://docs.gitlab.com/ee/api/issues.html
        return { 
                "Id": self.id,
                "Type": "Note" if self.system else "Comment",
                "Description": self.body, #pc.convert_text(self.body, "plain", format="md").strip(),
                "Attachment": self.attachment,
                "Author": self.author['name'],
                "Created": self.created_at,
                "Updated": self.updated_at
                }

    def get_links(self):
        links = dict(MARKDOWN_INLINE_LINK_RE.findall(self.body))
        return links
            
class Issues2csv:
    MAX_ISSUES = 10
    MAX_NOTES = 1000
    COLUMN_NAMES = ["Id", "Type", "Iid", "Title", "Description", "Status", "Due Date",
                    "Labels", "Milestone", "Assignees", "Author", "User Notes Count",
                    "URL", "Created", "Updated", "Attachment"]
    
    def __init__(self, args):

        self.gitlab_instance = args.gitlab_instance
        self.private_token = args.private_token
        self.project_id = args.project_id
        self.file_name = args.file_name
        # https://python-gitlab.readthedocs.io/en/stable/api-objects.html
        try:
            self.gl = gitlab.Gitlab(
                self.gitlab_instance,
                private_token = self.private_token)
        except gitlab.config.GitlabConfigMissingError as err:
            print(err)
        if os.path.isfile(self.file_name):
            os.remove(self.file_name)
    
    def export_csv(self, issues_dict):
        df = pd.DataFrame.from_dict(issues_dict, orient="index", columns=Issues2csv.COLUMN_NAMES)
        with open(self.file_name, 'a', encoding='utf-8') as f:
            df.to_csv(f, mode='a', header=f.tell()==0, sep='\t', encoding='utf-8')
    
    def export_excel(self, issues_dict):
        df = pd.DataFrame.from_dict(issues_dict, orient="index", columns=Issues2csv.COLUMN_NAMES)
        writer = ExcelWriter(self.file_name)
        df.to_excel(writer, 'Issues')
        writer.save()

    def save_attachments(self, baseurl, links):
        attachment_basedir = os.path.join(os.getcwd(), os.path.splitext(self.file_name)[0])
        if not os.path.exists(attachment_basedir):
            os.makedirs(attachment_basedir)
        for key, link in links.items():
            if not link.startswith('/uploads/'):
                continue # if not attachment, skip it
            attachment_path = os.path.join(attachment_basedir, os.path.normpath(link.replace("/uploads/", "")))
            attachment_dir = os.path.split(attachment_path)[0]
            if not os.path.exists(attachment_dir):
                os.makedirs(attachment_dir)            
            attachment_url = baseurl + link
            print(attachment_url, attachment_dir, attachment_path)
            
            request = urllib.request.Request(attachment_url, headers={'Private-Token': self.private_token})
            with urllib.request.urlopen(request) as response, open(attachment_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

    def main(self):
        project = self.gl.projects.get(self.project_id)
        if Issues2csv.MAX_ISSUES is not None:
            issues = project.issues.list(page=1, per_page=Issues2csv.MAX_ISSUES)
        else:
            issues = project.issues.list(all=True)
        issues_dict = {}

        for issue in issues:
            issue_obj = Issue(issue)
            issues_dict[issue_obj.iid * Issues2csv.MAX_NOTES] = issue_obj.to_dict()
            self.save_attachments(issue_obj.get_baseurl(), issue_obj.get_links())
            
            notes = issue.notes.list(all=True)[::-1]
            for i, note in enumerate(notes):
                note_obj = Note(note)
                issues_dict[issue_obj.iid * Issues2csv.MAX_NOTES + i + 1] = note_obj.to_dict()
                self.save_attachments(issue_obj.get_baseurl(), note_obj.get_links())
            
        if self.file_name.endswith('csv'):
            self.export_csv(issues_dict)
        else:
            self.export_excel(issues_dict)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="issues2csv", description="Generate a CSV file from GitLab issues.")
    parser.add_argument("gitlab_instance", help="URL of your GitLab instance, e.g. https://gitlab.com/")
    parser.add_argument("private_token", help="Access token for the API. You can generate one at Profile -> Settings")
    parser.add_argument("project_id", help="The ID of a GitLab project with issues", type=int)
    parser.add_argument("file_name", help="An individual file name for the export file.")
    args = parser.parse_args()

    i2c = Issues2csv(args)
    i2c.main()

