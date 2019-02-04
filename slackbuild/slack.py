import hmac
import json
import os.path
from string import Template
from slackbuild.config import Config
from slackclient import SlackClient


class Slack:

    VERSION = 'v0'

    def __init__(self, config: Config, client=None):
        self.__config = config.get('slack', {})
        # only get once instead of on each request
        self.__signing_secret = self.__config.get('signing_secret', '')

        self.__max_content_length = self.__config.get('webhook', {}).get('max_content_length', 50000)  # 50kB default

        if client is None:
            self.__client = SlackClient(self.__config.get('token', ''))
        else:
            self.__client = client

    def render_message(self, variables: dict, template='default.json'):
        """ constructs a dict representing a slack message from a json template

        Parameters:
            variables (dict) : substitutions used by builtin string.Template against json template
            template  (str)  : filename of message template to use

        Returns:
            (dict) : represents a slack message, used as input to post_message
        """
        if template == '':
            template = 'default.json'

        contents = '{}'
        with open(os.path.dirname(__file__) + '/../templates/' + template, 'r') as f:
            contents = f.read()

        temp = Template(contents)

        msg = temp.safe_substitute(variables, channel=self.__config.get('channel'))

        return json.loads(msg)

    def post_message(self, msg: dict):
        """ posts a message to the Slack API

        Parameters:
           msg (dict) : represents a message for python slack api client

        Returns:
           bool : true if slack API returned success
        """

        resp = self.__client.api_call("chat.postMessage", **msg)
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

        base = Slack.VERSION + ':' + ts + ':' + body

        sig = Slack.VERSION + '=' + hmac.new(
            bytes(self.__signing_secret, 'utf-8'),
            bytes(base, 'utf-8'),
            'sha256'
        ).hexdigest()

        if hmac.compare_digest(sig, req.headers.get('X-Slack-Signature', '')):
            return (True, '')

        return (False, 'Slack signature did not match')
