import json
from apiclient.discovery import build
from flask import Response
from flask import Request
from flask import abort
from slackbuild.build_status import BuildStatus
from slackbuild.colors import Colors
from slackbuild.command import Command
from slackbuild.config import Config
from slackbuild.slack import Slack

# create these as globals for reuse across non "cold starts"
config = Config()
slack = Slack(config)
# https://developers.google.com/apis-explorer/#p/cloudbuild/v1/
cloudbuild = build('cloudbuild', 'v1')


def slackbuild_webhook(req: Request):
    """ Slackbuild entrypoint when invoked via a slack webhook

    Parameters:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>

    Returns:
        str : a message to write to the log
    """
    global config
    global slack
    global cloudbuild

    # slack submits a POST
    if req.method != "POST":
        return abort(405)

    # not a true request from slack
    verified, err = slack.verify_webhook(req)
    if not verified:
        print(err)
        return abort(403)

    body = Slack.parse_request(req)
    argv = Slack.parse_command(body)
    msg = ""

    output, success = Command.run(argv, cloudbuild, config)

    if output is None:
        if success:
            # intentionaly not responding with a slack message
            return ('', 200)
        else:
            return abort(500)
    elif Slack.is_interactive_message(body):
        msg = slack.render_interactive_message(body, success, output)
    else:
        color = Colors.SUCCESS if success else Colors.FAILURE
        msg = slack.render_message({"result": output, "color": color}, "command.json")

    msg = json.dumps(msg)
    print(msg)
    return Response(response=msg, content_type="application/json")


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

    build, template = BuildStatus.toMessage(data, config)

    msg = slack.render_message(build, template)

    return slack.post_message(msg)
