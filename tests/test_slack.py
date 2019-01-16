import unittest
from slackbuild.config import Config
from slackbuild.slack import Slack

class TestSlack(unittest.TestCase):

    config_override = {
        'slack' : { 
            'channel' : '#test',
            'token'   : 'test',
            'signing_secret': '8f742231b10e8888abcd99yyyzzz85a5',
            'webhook' : {
                'max_content_length': 2
            }
        }
    }

    def test_post_message(self):
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
        mock_client = Mock_SlackClient("chat.postMessage", { "ok": True }, expected_args)

        slack = Slack(config, client=mock_client)

        success = slack.post_message(text="this is text", color="red", title="this is a title", footer="ID: 123")
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

        req = Mock_Request(headers, '', config.get('slack').get('webhook').get('max_content_length')+1)

        is_valid, err = slack.verify_webhook(req)
        self.assertFalse(is_valid)

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

    def get_data(self, as_text=True):
        return self.__body

if __name__ == '__main__':
    unittest.main()
