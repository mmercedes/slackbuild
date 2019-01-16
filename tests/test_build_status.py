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
        self.assertEqual(msg.get('title', ''), 'Build in my-project')
        self.assertEqual(msg.get('color', ''), BuildStatus.INFO)
        self.assertEqual(msg.get('footer', ''), 'ID: 2a246431 ')
        self.assertEqual(msg.get('text', ''), 'In progress | <https://console.cloud.google.com/gcr/builds/2a246431-3b50-4b00-8fc2-345f4d8f3fd8?project=123456789987|Logs>')
        
