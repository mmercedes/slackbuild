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
        self.assertEqual(msg.get('revision_url', ''), '')

    def test_get_valid_success_triggered(self):
        f = open('mocks/pubsub/success_triggered.json')
        data = json.load(f)
        f.close()

        msg, template = BuildStatus.toMessage(data, {})
        self.assertEqual(type(msg), dict)
        self.assertEqual(template, '')
        self.assertEqual(msg.get('project_id', ''), 'my-project')
        self.assertEqual(msg.get('build_color', ''), BuildStatus.SUCCESS)
        self.assertEqual(msg.get('build_id', ''), 'cc905bd4-4611-40f7-9811-ae28003e8216')
        self.assertEqual(msg.get('build_id_short', ''), 'cc905bd4')
        self.assertEqual(msg.get('build_status', ''), 'Finished successfully')
        self.assertEqual(msg.get('build_log_url', ''), 'https://console.cloud.google.com/gcr/builds/cc905bd4-4611-40f7-9811-ae28003e8216?project=1234567890')
        self.assertEqual(msg.get('build_duration', ''), '11 seconds')

        self.assertEqual(msg.get('repo_name', ''), 'testrepo')
        self.assertEqual(msg.get('revision', ''), '4f6fbcd4c4f7e90a0a290aae1e3e284eb770208d')
        self.assertEqual(msg.get('revision_sha_short', ''), '4f6fbcd4')
        self.assertEqual(msg.get('revision_url', ''), BuildStatus.CLOUD_SOURCE_URL % ('my-project', 'testrepo', '4f6fbcd4c4f7e90a0a290aae1e3e284eb770208d'))

    def test_get_valid_success_manual(self):
        f = open('mocks/pubsub/success_manual.json')
        data = json.load(f)
        f.close()

        msg, template = BuildStatus.toMessage(data, {'github_url': 'http://github.com/mmercedes'})
        self.assertEqual(type(msg), dict)
        self.assertEqual(template, '')
        self.assertEqual(msg.get('project_id', ''), 'my-project')
        self.assertEqual(msg.get('build_color', ''), BuildStatus.SUCCESS)
        self.assertEqual(msg.get('build_id', ''), 'b15157bc-232a-d4f3-738c-0e941bf2b5bd')
        self.assertEqual(msg.get('build_id_short', ''), 'b15157bc')
        self.assertEqual(msg.get('build_status', ''), 'Finished successfully')
        self.assertEqual(msg.get('build_log_url', ''), 'https://console.cloud.google.com/gcr/builds/b15157bc-232a-d4f3-738c-0e941bf2b5bd?project=1234567890')
        self.assertEqual(msg.get('build_duration', ''), '10 seconds')

        self.assertEqual(msg.get('repo_name', ''), 'testrepo')
        self.assertEqual(msg.get('revision', ''), '123')
        self.assertEqual(msg.get('revision_sha_short', ''), '123')
        self.assertEqual(msg.get('revision_url', ''), 'http://github.com/mmercedes/testrepo/commits/123')


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
