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

    @staticmethod
    def render_interactive_message(data, success, message):
        """ returns the original message, edited based on interaction success

        Parameters:
            data    (dict) : Request body from the slack interaction
            success (bool) : True if the intended interaction was succesful
            message (str)  : Message to include in replacement of the button

        Returns:
            (dict) : represents a slack message
        """

        if success:
            user = data.get('user', {}).get('id', '')
            user = '<@' + user + '>' if user else ''
            field = {
                "value": user + " " + message,
                "short": False
            }
        else:
            field = {
                "value": ":warning: " + message,
                "short": False
            }

        # explicitly not using dict.get() here as if this is not set there is either a logic error
        # or the slack request format has changed, and we need to update this code
        resp = data['original_message']
        # edit the original message in slack
        resp['replace_original'] = True

        attachments = resp.get('attachments', [])
        if len(attachments) > 0:
            # assume only one interaction allowed per message
            # remove all other actions from message
            for i in range(len(attachments)):
                a = attachments[i]
                if a.get('actions', {}) != {}:
                    resp['attachments'][i]['actions'] = []

            # overwrite the fields of the last attachment to include our message
            resp['attachments'][-1]['fields'] = [field]
        else:
            # not sure its possible to have an interactive message without any attachments
            # but just in case
            resp['attachments'] = {'fields': [field]}

        return resp

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

    @staticmethod
    def is_interactive_message(data):
        """ Check if Request data is from an interactive slack message or a /slash command

        Parameters:
            data (dict) : Request body

        Returns:
            bool : true if the request is from an interactive message

        See: https://api.slack.com/docs/message-buttons
        """
        # to avoid parsing json everytime, do a simple check for the string
        # for now assume we dont receive slack requests with a "payload" field
        # other than when its an interactive message
        return data.get('type', '') == 'interactive_message'

    @staticmethod
    def parse_command(data):
        """ Parse a slack Request body into arguments for Command.run

        Parameters:
           data (dict) : Request body

        Returns:
           list : arguments
        """
        interactive = Slack.is_interactive_message(data)

        if interactive:
            actions = data.get('actions', [])
            text = actions[0].get('value', '') if len(actions) > 0 else ''
        else:
            text = data.get("text", "")

        argv = text.strip().split(' ')
        argv = [a.strip() for a in argv if a.strip() is not '']

        return argv

    @staticmethod
    def parse_request(req):
        """ Turns a Request into a dict of slack hook parameters

        Parameters:
            req (Request) : flask Request object that triggered cloud function

        Returns:
            dict : slack hook parameters

        """
        data = req.form.to_dict()
        payload = data.get('payload', '')
        if payload != '':
            data = json.loads(payload)
        return data
