#!/home/duerkop/.virtualenvs/gitlab/bin/python3

import pypandoc as pc
import os
import gitlab
import pandas as pd
from datetime import date, datetime, time, timedelta
import argparse


class Milestone:

    def __init__(self, milestone):
        self.iid = milestone['iid']
        self.title = milestone['title']

    
    def __str__(self):
        return self.title


    def to_dict(self):
        return  { self.iid:
            {
                "Titel": self.title
            }
        }


class Issue:

    def __init__(self, issue):
        self.iid = issue.attributes['iid']
        self.title = issue.attributes['title']
        self.description = issue.attributes['description'] or ""
        self.state = issue.attributes['state']
        self.created_at = issue.attributes['created_at']
        self.updated_at = issue.attributes['updated_at']
        self.closed_at = issue.attributes['closed_at']
        self.closed_by = issue.attributes['closed_by']
        self.labels = issue.attributes['labels']
        self.milestone = issue.attributes['milestone']
        self.author = issue.attributes['author']
        self.due_date = issue.attributes['due_date']
        self.web_url = issue.attributes['web_url']


    def __str__(self):
        return self.title

    
    def to_dict(self):

        milestone = "nicht zugewiesen"

        if self.milestone is not None:
            milestone = Milestone(self.milestone)

        return { self.iid: 
            { 
                "Titel": self.title,
                "Beschreibung": pc.convert_text(self.description, "plain", format="md").strip(),
                "Status": self.state,
                "Fällig am": self.due_date,
                "Labels": self.labels,
                "Meilenstein": milestone,
                "Autor_in": self.author['name'],
                "URL": self.web_url,
                "Erstellt": self.created_at,
                "Geändert": self.updated_at,
                "Geschlossen am": self.closed_at,
                "Geschlossen von": self.closed_by
                }
        }

class Issues2csv:

    def __init__(self, args):

        self.gitlab_instance = args.gitlab_instance
        self.private_token = args.private_token
        self.project_id = args.project_id
        self.file_name = args.file_name

        try:
            self.gl = gitlab.Gitlab(
                self.gitlab_instance,
                private_token = self.private_token)
        except gitlab.config.GitlabConfigMissingError as err:
            print(err)
        if os.path.isfile(self.file_name):
            os.remove(self.file_name)
    
    def export_csv(self, d):
        df = pd.DataFrame.from_dict(d, orient="index")
        with open(self.file_name, 'a') as f:
            df.to_csv(f, mode='a', header=f.tell()==0, sep='\t', encoding='utf-8')


    def main(self):
        project = self.gl.projects.get(self.project_id)
        issues = project.issues.list(all=True)

        for i in issues:
            print(Issue(i).closed_by)
            issue = Issue(i).to_dict()

            # print(issue)
            self.export_csv(issue)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="issues2csv", description="Generate a CSV file from GitLab issues.")
    parser.add_argument("gitlab_instance", help="URL of your GitLab instance, e.g. https://gitlab.com/")
    parser.add_argument("private_token", help="Access token for the API. You can generate one at Profile -> Settings")
    parser.add_argument("project_id", help="The ID of a GitLab project with issues", type=int)
    parser.add_argument("file_name", help="An individual file name for the export file.")
    args = parser.parse_args()

    i2c = Issues2csv(args)
    i2c.main()

