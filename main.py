from slackbuild.build_status import BuildStatus
from slackbuild.config import Config
from slackbuild.slack import Slack
from flask import Request
from flask import Response


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

    is_valid, err = slack.verify_webhook(req)
    if not is_valid:
        return err

    return 'hello world'

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

    print('TESTSTSFDGDFG')

    build = BuildStatus.toMessage(data)

    return slack.post_message(**build)
