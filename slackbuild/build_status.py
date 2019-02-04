import base64
import json
from dateutil import parser

"""
   Wrapper for the Build.Status response from the Google CloudBuild API
   https://cloud.google.com/cloud-build/docs/api/reference/rest/v1/projects.builds#Build.Status
"""


class BuildStatus:

    CLOUD_SOURCE_URL = 'https://source.cloud.google.com/%s/%s/+/%s'

    """
     hex code for color of slack message attachment
     https://api.slack.com/docs/message-attachments
    """
    UNKNOWN = '#d3d3d3'  # grey
    INFO = '#1a73e8'     # blue
    WARN = '#f09300'     # orange
    SUCCESS = '#00c752'  # green
    FAILURE = '#da4236'  # red

    statuses = {
        'STATUS_UNKNOWN': ('Status of the build is unknown', UNKNOWN),
        'QUEUED': ('Queued', UNKNOWN),
        'WORKING': ('In progress', INFO),
        'SUCCESS': ('Finished successfully', SUCCESS),
        'FAILURE': ('Failed', FAILURE),
        'INTERNAL_ERROR': ('Failed due to an internal error', FAILURE),
        'TIMEOUT': ('Timed out', UNKNOWN),
        'CANCELLED': ('Cancelled', UNKNOWN)
    }

    @staticmethod
    def toMessage(data, config):
        """ Generate a cloud build status and message from a pubsub message

        Parameters:
            data (dict): see https://cloud.google.com/pubsub/docs/reference/rest/v1/PubsubMessage

        Returns:
            (dict, str) : dict is input args for Slack.render_message(), str is template filename is configured
        """

        variables = {}

        variables['build_id'] = data.get("attributes", {}).get("buildId", "UNKNOWN")
        variables['build_id_short'] = variables['build_id'].split('-')[0]

        status = data.get("attributes", {}).get("status", "")
        build = BuildStatus.__decode_data(data.get("data", None))

        (variables['build_status'], variables['build_color']) = BuildStatus.statuses.get(status, ('Invalid status', BuildStatus.FAILURE))

        variables['project_id'] = build.get('projectId', 'unknown project id')
        variables['build_log_url'] = build.get('logUrl', '')

        variables = BuildStatus.__add_timing(build, variables)
        variables = BuildStatus.__add_git_info(build, variables, config)

        template = config.get('slack', {}).get('templates', {}).get('default', '')
        template = config.get('slack', {}).get('templates', {}).get(status.lower(), template)

        return variables, template

    @staticmethod
    def __add_timing(build, variables):
        start = build.get('startTime', None)
        end = build.get('finishTime', None)

        variables['build_duration'] = ''
        if start is not None and end is not None:
            delta = parser.parse(end) - parser.parse(start)
            variables['build_duration'] = str(delta.seconds) + ' seconds'

        return variables

    @staticmethod
    def __add_git_info(build, variables, config):
        # prefer `sourceProvenance` over `source`
        repoSource = build.get('sourceProvenance', {}).get('resolvedRepoSource', {})
        if not bool(repoSource):
            repoSource = build.get('source', {}).get('repoSource', {})
            # prefer both of those over _GIT_SHA, _BRANCH, _REPO substitutions
            if not bool(repoSource):
                repoSource = {}
                repoSource['repoName'] = build.get('substitutions', {}).get('_REPO', '')
                repoSource['commitSha'] = build.get('substitutions', {}).get('_GIT_SHA', '')
                repoSource['branchName'] = build.get('substitutions', {}).get('_BRANCH', '')

        variables['repo_name'] = repoSource.get('repoName', '')
        # prefer sha over branch as revision in case both are set
        sha = repoSource.get('commitSha', '')
        if sha is not '':
            variables['revision'] = sha
            variables['revision_sha_short'] = sha[:8]
        else:
            variables['revision'] = repoSource.get('branchName', '')
            variables['revision_sha_short'] = variables['revision']

        variables['revision_url'] = ''
        if variables['repo_name'] is not '' and variables['revision'] is not '':
            github_url = config.get('github_url', '')
            if github_url is not '':
                url = "%s/%s/commits/%s" % (github_url, variables['repo_name'], variables['revision'])
            # assume this is a CloudSource repo
            else:
                url = BuildStatus.CLOUD_SOURCE_URL % (build.get('projectId', ''), variables['repo_name'], variables['revision'])

            variables['revision_url'] = url

        return variables

    @staticmethod
    def __decode_data(data):
        if data is None:
            return {}

        tmp = base64.b64decode(data).decode("utf-8")
        tmp = json.loads(tmp)
        return tmp
