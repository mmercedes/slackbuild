import base64
import json
from dateutil import parser

"""
   Wrapper for the Build.Status response from the Google CloudBuild API
   https://cloud.google.com/cloud-build/docs/api/reference/rest/v1/projects.builds#Build.Status
"""
class BuildStatus:

    # hex code for color of slack message attachment
    # https://api.slack.com/docs/message-attachments
    UNKNOWN = '#d3d3d3' # grey
    INFO    = '#00bfff' # blue
    WARN    = '#ffff00' # yellow
    SUCCESS = '#32cd32' # green
    FAILURE = '#ff0000' # red

    statuses = {
        'STATUS_UNKNOWN': ('Status of the build is unknown', UNKNOWN),
        'QUEUED':         ('Queued', UNKNOWN),
        'WORKING':        ('In progress', INFO),
        'SUCCESS':        ('Finished successfully', SUCCESS),
        'FAILURE':        ('Failed', FAILURE),
        'INTERNAL_ERROR': ('Failed due to an internal error', FAILURE),
        'TIMEOUT':        ('Timed out', UNKNOWN),
        'CANCELLED':      ('Cancelled', UNKNOWN)
    }

    @staticmethod
    def toMessage(data):
        """ Generate a cloud build status and message from a pubsub message

        Parameters:
            data (dict): see https://cloud.google.com/pubsub/docs/reference/rest/v1/PubsubMessage

        Returns:
            (dict) : input args for Slack.post_message()
        """
        buildId = data.get("attributes", {}).get("buildId", "UNKNOWN").split('-')[0]
        status = data.get("attributes", {}).get("status", "")
        build = BuildStatus.__decode_data(data.get("data", None))

        (msg, color) =  BuildStatus.statuses.get(status, ('Invalid status', BuildStatus.FAILURE))

        start = build.get('startTime', None)
        end = build.get('finishTime', None)

        took = ''
        if start is not None and end is not None:
            delta = parser.parse(end) - parser.parse(start)
            took = '| ' + str(delta.seconds) + ' seconds'

        projectId = build.get('projectId', 'unknown project id')

        link = ''
        logUrl = build.get('logUrl', '')
        if logUrl is not '':
            link = f' | <{logUrl}|Logs>'

        msg = msg + link
        message = {
            "title": f'Build in {projectId}',
            "color": color,
            "text": msg,
            "footer": f'ID: {buildId} {took}'
        }

        return message

    @staticmethod
    def __decode_data(data):
        if data is None:
            return {}

        tmp = base64.b64decode(data).decode("utf-8") 
        tmp = json.loads(tmp)
        return tmp
        