import unittest
import gitlab
from .gldates2ics import Milestones2ics
from datetime import date, datetime, time

class TestMilestones2ics(unittest.TestCase):

    def setUp(self):
        self.m2i = Milestones2ics() 


    def test_convert_timestamp_for_ical(self):
        ts = self.m2i.convert_timestamp_for_ical("2019-02-09")
        self.assertEqual(ts, datetime(2019,2,9,0,0,0))


    def test_fetch_projects(self):
        projects = self.m2i.fetch_projects()
        self.assertNotEqual(len(projects), 0, "No projects found!")


    def test_fetch_groups(self):
        groups = self.m2i.fetch_groups()
        self.assertNotEqual(len(groups), 0, "No groups found!")


    @unittest.skip("Not testable as everybody has different IDs")
    def test_fetch_group(self):
        group = self.m2i.fetch_group(811)
        self.assertIs(type(group), gitlab.v4.objects.Group)


    def test_make_readable(self):
        pass

if __name__ == "__main__":
    unittest.main()

