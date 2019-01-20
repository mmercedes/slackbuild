from build_status import BuildStatus
from config import Config
from flask import Request
from slack import Slack


# create these as globals for reuse across non "cold starts"
config = Config()
slack = Slack(config)
gcb = ''

def slackbuild_webhook(req: Request):
    """ Slackbuild entrypoint when invoked via a slack webhook

    Parameters:
        data   (dict) : Pubsub Message
        context (obj) : Context object for this event

    Returns:
        str : a message to write to the log
    """

    global config
    global slack

    return ''

def slackbuild_pubsub(data, context):
    """ Slackbuild entrypoint when invoked via a cloudbuild pubsub message

    Parameters:
        data   (dict) : Pubsub Message
        context (obj) : Context object for this event

    Returns:
        str : a message to write to the log
    """
    global config
    global slack

    print(data)
    print(context)

    build = BuildStatus.toMessage(data, config)

    msg = slack.render_message(build)

    return slack.post_message(msg)
