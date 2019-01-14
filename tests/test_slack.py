import unittest
from slackbuild.config import Config
from slackbuild.slack import Slack

class TestSlack(unittest.TestCase):

    config_override = {
        'slack' : { 
            'channel' : '#test',
            'token'   : 'test'
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

class Mock_SlackClient():

    def __init__(self, call, response, call_args={}):
        self.__call = call
        self.__response = response
        self.__call_args = call_args

    def api_call(self, call, **args):
        assert self.__call == call
        assert self.__call_args == args
        return self.__response


if __name__ == '__main__':
    unittest.main()
