import unittest
from config import Config
from slack import Slack

class TestSlack(unittest.TestCase):

    config_override = {
        'slack_channel' : '#test',
        'slack_token'   : 'test'
    }

    def test_message(self):
        config = Config(config_override=self.config_override)
        slack = Slack(config)

        expected = {
            "attachments": [
                {
                    "fallback": "this is text",
                    "color": "good",
                    "text": "this is text"
                }
            ],
            "channel": "#test"
        }            

        actual = slack.message("this is text", "good")
        self.assertEqual(expected, actual)

    def test_send(self):
        config = Config(config_override=self.config_override)
        expected = '{ "ok": true}'
        mock_client = Mock_SlackClient("chat.postMessage", expected)
        slack = Slack(config, mock_client)

        self.assertEqual(expected, slack.send('foo', 'bar'))

class Mock_SlackClient():

    def __init__(self, call, response):
        self.__call = call
        self.__response = response

    def api_call(self, call, **args):
        assert self.__call == call
        return self.__response


if __name__ == '__main__':
    unittest.main()
