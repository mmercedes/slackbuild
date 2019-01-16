import hmac
import json
from slackbuild.config import Config
from slackclient import SlackClient

class Slack:

    VERSION = 'v0'

    def __init__(self, config: Config, client=None):
        self.__config = config.get('slack', {})
        # only get once instead of on each request
        self.__signing_secret = self.__config.get('signing_secret', '')

        self.__max_content_length = self.__config.get('webhook', {}).get('max_content_length', 50000) # 50kB default

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


    def verify_webhook(self, req):
        """ Verifies req is from slack
        See: https://api.slack.com/docs/verifying-requests-from-slack

        Parameter:
            req (flask.Request) : the request object

        Returns:
            (bool, str) : bool is true if request is verified, str is a log message when invalid request
        """

        if req.content_length > self.__max_content_length or req.content_length <= 0:
            return (False, 'Webhook request body is greater than slack.webhook.max_content_length')

        body = req.get_data(as_text=True)

        ts = req.headers.get('X-Slack-Request-Timestamp', '')

        base = Slack.VERSION +':'+ ts +':'+ body

        sig = Slack.VERSION +'='+ hmac.new(
            bytes(self.__signing_secret, 'utf-8'),
            bytes(base, 'utf-8'),
            'sha256'
        ).hexdigest()

        if hmac.compare_digest(sig, req.headers.get('X-Slack-Signature', '')):
            return (True, '')

        return (False, 'Slack signature did not match')
