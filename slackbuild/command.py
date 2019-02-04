from slackbuild.config import Config
from googleapiclient.errors import HttpError


class Command:

    BAD_INPUT = 'Unrecognized command'

    @staticmethod
    def parse(data):
        argv = data.get("text", "").strip().split(' ')
        argv = [a.strip() for a in argv if a.strip() is not '']

        return argv

    @staticmethod
    def run(data, cloudbuild, config: Config):
        argv = Command.parse(data)

        if argv == []:
            return {"result": Command.BAD_INPUT}

        cmd = argv[0].lower()
        argv = argv[1:] if len(argv) > 1 else []
        resp = None

        project = config.get('gcloud', {}).get('project_id', '')

        if cmd == 'cancel':
            resp = Command.cancel(argv, cloudbuild, project)
        elif cmd == 'retry':
            resp = Command.retry(argv, cloudbuild, project)
        # elif cmd == 'trigger':
        #    resp =  Command.submit(argv, cloudbuild, config)
        else:
            resp = Command.BAD_INPUT

        return {"result": str(resp)} if resp else None

    @staticmethod
    def cancel(argv: list, cloudbuild, project):
        """
        See: https://cloud.google.com/cloud-build/docs/api/reference/rest/v1/projects.builds/cancel
        """
        buildId = argv[0] if len(argv) > 0 else ""

        if project == "" or buildId == "":
            return "Usage: cancel <buildId>"

        method = cloudbuild.projects().builds().cancel(projectId=project, id=buildId)

        status, msg = Command._api_call(method)

        if status == "200":
            return "Build cancelled"
        elif status == "404":
            return "No build found in %s with ID %s" % (project, buildId)

        print("Unhandled status : %s - %s" % (status, msg))
        return msg

    @staticmethod
    def retry(argv: list, cloudbuild, project):
        """
        See: https://cloud.google.com/cloud-build/docs/api/reference/rest/v1/projects.builds/retry
        """
        buildId = argv[0] if len(argv) > 0 else ""

        if project == "" or buildId == "":
            return "Usage: retry <buildId>"

        method = cloudbuild.projects().builds().retry(projectId=project, id=buildId)

        status, msg = Command._api_call(method)

        if status == "200":
            return "Submitted retry request"
        elif status == "404":
            return "No build found in %s with ID %s" % (project, buildId)

        print("Unhandled status : %s - %s" % (status, msg))
        return msg

    @staticmethod
    def trigger(argv: list, cloudbuild, project):

        return None

    @staticmethod
    def _api_call(method):
        try:
            op = method.execute()

            done = op.get("done", False)
            if done and op.get("error", {}) != {}:
                return "0", op.get("error").get("message", "Unknown error")

        except HttpError as err:
            return str(err.resp.status), err._get_reason()

        return "200", ""
