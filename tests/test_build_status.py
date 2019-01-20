import json
import unittest
from slackbuild.build_status import BuildStatus
from slackbuild.config import Config

class TestBuildStatus(unittest.TestCase):

    def test_get_invalid(self):
        msg, template = BuildStatus.toMessage({}, {})
        self.assertEqual(type(msg), dict)
        self.assertNotEqual(msg, {})
        self.assertEqual(template, '')

    def test_get_valid_working(self):
        f = open('mocks/pubsub/working_manual.json')
        data = json.load(f)
        f.close()

        msg, template = BuildStatus.toMessage(data, {})
        self.assertEqual(type(msg), dict)
        self.assertEqual(template, '')
        self.assertEqual(msg.get('project_id', ''), 'my-project')
        self.assertEqual(msg.get('build_color', ''), BuildStatus.INFO)
        self.assertEqual(msg.get('build_id', ''), '2a246431-3b50-4b00-8fc2-345f4d8f3fd8')
        self.assertEqual(msg.get('build_id_short', ''), '2a246431')
        self.assertEqual(msg.get('build_status', ''), 'In progress')
        self.assertEqual(msg.get('build_log_url', ''), 'https://console.cloud.google.com/gcr/builds/2a246431-3b50-4b00-8fc2-345f4d8f3fd8?project=123456789987')
        self.assertEqual(msg.get('build_duration', ''), '')
        
    def test_template_config(self):

        for status in BuildStatus.statuses.keys():

            config_override = {
                'slack' : {
                    'templates' : {
                        status.lower() : status.lower() + '.json'
                    }
                }
            }

            data = {
                'attributes': {
                    'status': status
                }
            }

            config = Config(config_override=config_override)
            msg, template = BuildStatus.toMessage(data, config)

            self.assertEqual(template, status.lower() + '.json')


        config_override = {
            'slack' : {
                'templates' : {
                    'default': 'foo.json'
                    }
            }
        }

        data = {
            'attributes': {
                'status': 'SUCCESS'
            }
        }

        config = Config(config_override=config_override)
        msg, template = BuildStatus.toMessage(data, config)
        self.assertEqual(template, 'foo.json')
