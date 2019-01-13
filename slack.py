import json
from config import Config
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
            str : log line indicating message success or failure
        """

        msg = self.message(text, level)

        return self.__client.api_call("chat.postMessage", **msg)


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

