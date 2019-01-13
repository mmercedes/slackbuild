import json
from config import Config
#from flask import Request
from slackclient import SlackClient

class Slack:

    def __init__(self, config: Config, client=None):
        self.__config = config
        if client is None:
            self.__client = SlackClient(self.__config.get('slack_token'))
        else:
            self.__client = client

    def send(self, text: str, level: str):
        """ sends a message to Slack
    
        Parameters:
            text  (str) : text to include in the message
            level (str) : one of 'good', 'warning', 'danger', or '' that determines message color

        Returns:
            bool : true if slack API returned success
        """

        msg = self.message(text, level)

        resp = self.__client.api_call("chat.postMessage", **msg)
        print(resp)
        return resp.get('ok', False)


    def message(self, text: str, level: str):
        """ constructs a dict representing a message in the Slack API

        Parameters:
            text  (str) : text to include in the message
            level (str) : one of 'good', 'warning', 'danger', or '' that determines message color

        Returns:
           dict : a message for the Slack API
        """

        return {
            "attachments": [
                {
                    "fallback": text,
                    "color": level,
                    "text": text
                }
            ],
            "channel": self.__config.get('slack_channel')
        }


#    def verify_webhook(req: Request):
