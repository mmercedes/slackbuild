import json
from config import Config
#from flask import Request
from slackclient import SlackClient

class Slack:

    def __init__(self, config: Config, client=None):
        self.__config = config.get('slack', {})
        if client is None:
            self.__client = SlackClient(self.__config.get('token', ''))
        else:
            self.__client = client

    def post_message(self, text='', color='', title='', footer=''):
        """ constructs a dict representing a message in the Slack API

        Parameters:
            text  (str) : text to include in the message
            color (str) : hex string for message color
            title (str) : prepended to message text in bold

        Returns:
           bool : true if slack API returned success
        """

        message = {
            "attachments": [
                {
                    "title": title,
                    "fallback": text,
                    "text": text,
                    "color": color,
                    "footer": footer
                }
            ],
            "channel": self.__config.get('channel')
        }

        resp = self.__client.api_call("chat.postMessage", **message)
        print(resp)
        return resp.get('ok', False)


#    def verify_webhook(req: Request):
