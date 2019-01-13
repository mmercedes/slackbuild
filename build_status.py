"""
   Wrapper for the Build.Status response from the Google CloudBuild API
   https://cloud.google.com/cloud-build/docs/api/reference/rest/v1/projects.builds#Build.Status
"""
class BuildStatus:

    # hex code for color of slack message attachment
    # https://api.slack.com/docs/message-attachments
    UNKNOWN = '#808080' # grey 
    INFO    = '#0000ff' # blue
    WARN    = '#ffff00' # yellow
    SUCCESS = '#008000' # green
    FAILURE = '#ff0000' # red

    statuses = {
        'STATUS_UNKNOWN': ('Status of the build is unknown', BuildStatus.UNKNOWN),
        'QUEUED':         ('Build is queued', BuildStatus.INFO),
        'WORKING':        ('Build is in progress', BuildStatus.INFO),
        'SUCCESS':        ('Build finished successfully', BuildStatus.SUCCESS),
        'FAILURE':        ('Build failed', BuildStatus.FAILURE),
        'INTERNAL_ERROR': ('Build failed due to an internal error', BuildStatus.FAILURE),
        'TIMEOUT':        ('Build timed out', BuildStatus.UNKNOWN),
        'CANCELLED':      ('Build was cancelled', BuildStatus.UNKNOWN)
    }

    @staticmethod
    def fromMessage(data):
        """ Generate a cloud build status and message from a pubsub message

        Parameters:
            data (dict): see https://cloud.google.com/pubsub/docs/reference/rest/v1/PubsubMessage

        Returns:
            (str, str) : tuple value from one of BuildStatus.statuses 
        """
        buildId = data.get('attributes', {}).get('buildId', 'UNKNOWN')
        status = data.get('attributes', {}).get('status', '')

        (msg, color) =  BuildStatus.statuses.get(status, ('Invalid status', BuildStatus.FAILURE))

        msg = f'{buildId} : {msg}'

        return (msg, color)
