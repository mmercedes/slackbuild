import json
import unittest
from slackbuild.build_status import BuildStatus

class TestBuildStatus(unittest.TestCase):

    def test_get_invalid(self):
        msg = BuildStatus.toMessage({})
        self.assertEqual(type(msg), dict)
        self.assertNotEqual(msg, {})

    def test_get_valid_working(self):
        f = open('mocks/pubsub/working_data.json')
        data = json.load(f)
        f.close()

        msg = BuildStatus.toMessage(data)
        self.assertEqual(type(msg), dict)
        self.assertEqual(msg.get('project_id', ''), 'my-project')
        self.assertEqual(msg.get('build_color', ''), BuildStatus.INFO)
        self.assertEqual(msg.get('build_id', ''), '2a246431-3b50-4b00-8fc2-345f4d8f3fd8')
        self.assertEqual(msg.get('build_id_short', ''), '2a246431')
        self.assertEqual(msg.get('build_status', ''), 'In progress')
        self.assertEqual(msg.get('build_log_url', ''), 'https://console.cloud.google.com/gcr/builds/2a246431-3b50-4b00-8fc2-345f4d8f3fd8?project=123456789987')
        self.assertEqual(msg.get('build_duration', ''), '')
        
