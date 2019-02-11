import json
import unittest
from slackbuild.config import Config
from slackbuild.slack import Slack


class TestSlack(unittest.TestCase):

    config_override = {
        'slack': {
            'channel': '#test',
            'token': 'test',
            'signing_secret': '8f742231b10e8888abcd99yyyzzz85a5',
            'webhook': {
                'max_content_length': 2
            }
        }
    }

    def test_render_message_default(self):
        config = Config(config_override=self.config_override)

        variables = {
            "build_color": "#FFFFFF",
            "build_id": "1234567890",
            "build_id_short": "1234",
            "build_log_url": "http://google.com",
            "build_status": "In Progress",
            "build_duration": "3 seconds",
            "project_id": "my-project",
            "repo_name": "testrepo",
            "revision_url": "github.com/test/testrepo/commits/123",
            "revision": "123",
            "revision_sha_short": "123"
        }

        expected = {
            "attachments": [
                {
                    "text": "*testrepo*  <github.com/test/testrepo/commits/123|123>\nIn Progress | <http://google.com|Logs>",
                    "fallback": "In Progress | <http://google.com|Logs>",
                    "color": "#FFFFFF",
                    "footer": "ID: 1234 3 seconds",
                    "mrkdwn_in": ["text"]
                }
            ],
            "channel": "#test"
        }

        mock_client = Mock_SlackClient("", "", {})
        slack = Slack(config, client=mock_client)
        actual = slack.render_message(variables)

        self.assertEqual(actual, expected)

    def test_post_message_success(self):
        config = Config(config_override=self.config_override)

        expected_args = {
            "attachments": [
                {
                    "title": "this is a title",
                    "fallback": "this is text",
                    "text": "this is text",
                    "color": "red",
                    "footer": "ID: 123"
                }
            ],
            "channel": "#test"
        }
        mock_client = Mock_SlackClient("chat.postMessage", {"ok": True}, expected_args)

        slack = Slack(config, client=mock_client)

        success = slack.post_message(expected_args)
        self.assertTrue(success)

    def test_verify_webhook_valid(self):
        config = Config(config_override=self.config_override)
        # Assert Slack.verify_webhook doesn't make an API call
        mock_client = Mock_SlackClient("", "", {})
        slack = Slack(config, client=mock_client)

        headers = {
            'X-Slack-Request-Timestamp': '1531420618',
            'X-Slack-Signature': 'v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503'
        }

        body = 'token=xyzz0WbapA4vBCDEFasx0q6G&team_id=T1DC2JH3J&team_domain=testteamnow&channel_id=G8PSS9T3V&channel_name=foobar&user_id=U2CERLKJA&user_name=roadrunner&command=%2Fwebhook-collect&text=&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT1DC2JH3J%2F397700885554%2F96rGlfmibIGlgcZRskXaIFfN&trigger_id=398738663015.47445629121.803a0bc887a14d10d2c447fce8b6703c'

        req = Mock_Request(headers, body, 1)

        is_valid, err = slack.verify_webhook(req)
        self.assertTrue(is_valid)

    def test_verify_webhook_invalid(self):
        config = Config(config_override=self.config_override)
        # Assert Slack.verify_webhook doesn't make an API call
        mock_client = Mock_SlackClient("", "", {})
        slack = Slack(config, client=mock_client)

        headers = {
            'X-Slack-Request-Timestamp': '1531420619',
            'X-Slack-Signature': 'v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503'
        }

        body = 'token=xyzz0WbapA4vBCDEFasx0q6G&team_id=T1DC2JH3J&team_domain=testteamnow&channel_id=G8PSS9T3V&channel_name=foobar&user_id=U2CERLKJA&user_name=roadrunner&command=%2Fwebhook-collect&text=&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT1DC2JH3J%2F397700885554%2F96rGlfmibIGlgcZRskXaIFfN&trigger_id=398738663015.47445629121.803a0bc887a14d10d2c447fce8b6703c'

        req = Mock_Request(headers, body, 1)

        is_valid, err = slack.verify_webhook(req)
        self.assertFalse(is_valid)

    def test_verify_webhook_max_content_length(self):
        config = Config(config_override=self.config_override)
        # Assert Slack.verify_webhook doesn't make an API call
        mock_client = Mock_SlackClient("", "", {})
        slack = Slack(config, client=mock_client)

        headers = {
            'X-Slack-Request-Timestamp': '1531420618',
            'X-Slack-Signature': 'v0=a2114d57b48eac39b9ad189dd8316235a7b4a8d21a10bd27519666489c69b503'
        }

        req = Mock_Request(headers, '', config.get('slack').get('webhook').get('max_content_length') + 1)

        is_valid, err = slack.verify_webhook(req)
        self.assertFalse(is_valid)

    def test_is_interactive_message(self):
        self.assertTrue(Slack.is_interactive_message({"type": "interactive_message"}))
        self.assertFalse(Slack.is_interactive_message({"type": "interactive-message"}))
        self.assertFalse(Slack.is_interactive_message({"type": ""}))
        self.assertFalse(Slack.is_interactive_message({}))

    def test_parse_command(self):
        cases = [
            ("retry e36544dc-82a1-cc63-bac7-a6b2d18d7ea6", ["retry", "e36544dc-82a1-cc63-bac7-a6b2d18d7ea6"]),
            ("   ", []),
            (" a b  c ", ["a", "b", "c"])
        ]

        actual = Slack.parse_command({})

        self.assertEqual([], actual)

        for case in cases:
            text, expected = case
            # try as a /slash command input
            input = {"text": text}
            actual = Slack.parse_command(input)
            self.assertEqual(expected, actual)
            # try as an interactive message input
            input = {"type": "interactive_message", "actions": [{"value": text}]}
            actual = Slack.parse_command(input)
            self.assertEqual(expected, actual)

    def test_parse_request(self):
        f = open('mocks/webhook/interactive_message.json')
        payload = json.load(f)
        f.close()
        f = open('mocks/webhook/interactive_message_payload.json')
        expected = json.load(f)
        f.close()
        f = open('mocks/webhook/form.json')
        form = json.load(f)
        f.close()

        req = Mock_Request('', payload, 1)
        self.assertEqual(expected, Slack.parse_request(req))

        req = Mock_Request('', form, 1)
        self.assertEqual(form, Slack.parse_request(req))

        req = Mock_Request('', {}, 1)
        self.assertEqual({}, Slack.parse_request(req))

    def test_render_interactive_message(self):
        self.maxDiff = None

        f = open('mocks/webhook/interactive_message_payload.json')
        data = json.load(f)
        f.close()

        expected = {'type': 'message', 'subtype': 'bot_message', 'text': '', 'ts': '1549843673.001900', 'username': 'slackbuild', 'bot_id': 'BZAB1CDE3', 'attachments': [{'callback_id': 'placeholder', 'fallback': 'Queued | <https://console.cloud.google.com/gcr/builds/ec52f443-1f02-5d9b-bda7-1093162bcbf9?project=123456789098|Logs>', 'text': '*testrepo*  <https://source.cloud.google.com/my-project-id/testrepo/+/ab12cd34|ab12cd34>\nQueued | <https://console.cloud.google.com/gcr/builds/ec52f443-1f02-5d9b-bda7-1093162bcbf9?project=123456789098|Logs>', 'title': 'Build in my-project-id', 'footer': 'ID: ec52f443 ', 'id': 1, 'color': 'd3d3d3', 'actions': [], 'mrkdwn_in': ['text']}], 'replace_original': True}

        expected['attachments'][-1]['fields'] = [{'value': '<@UAB1C2DE3> cancelled build', 'short': False}]

        self.assertEqual(expected, Slack.render_interactive_message(data, True, 'cancelled build'))

        expected['attachments'][-1]['fields'] = [{'value': ':warning: failed to cancel build', 'short': False}]

        self.assertEqual(expected, Slack.render_interactive_message(data, False, 'failed to cancel build'))


class Mock_SlackClient():

    def __init__(self, call, response, call_args={}):
        self.__call = call
        self.__response = response
        self.__call_args = call_args

    def api_call(self, call, **args):
        assert self.__call == call
        assert self.__call_args == args
        return self.__response


class Mock_Request():

    def __init__(self, headers, body, content_length):
        self.headers = headers
        self.__body = body
        self.content_length = content_length
        self.form = self

    def get_data(self, as_text=True):
        return self.__body

    def to_dict(self):
        return self.__body


if __name__ == '__main__':
    unittest.main()
