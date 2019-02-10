from slackbuild.config import Config
from googleapiclient.errors import HttpError


class Command:

    BAD_INPUT = "Unrecognized command\nSee '/builds help' for available commands"

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
        elif cmd == 'help':
            resp = Command.help()
        # elif cmd == 'trigger':
        #    resp =  Command.submit(argv, cloudbuild, config)
        else:
            resp = Command.BAD_INPUT

        return {"result": str(resp)} if resp else None

    @staticmethod
    def help():
        return "```" + \
               "/builds <command> [arguments]\\n" + \
               "/builds retry <buildId>    Retry a failed build\\n" + \
               "/builds cancel <buildId>   Cancel a build in progress\\n" + \
               "/builds help               Show this message\\n" + \
               "```"

    @staticmethod
    def cancel(argv: list, cloudbuild, project):
        """
        See: https://cloud.google.com/cloud-build/docs/api/reference/rest/v1/projects.builds/cancel
        """
        buildId = argv[0] if len(argv) > 0 else ""

        if project == "" or buildId == "":
            return "Usage: cancel <buildId>"

        if len(buildId) < 36:
            return "Invalid build ID"

        method = cloudbuild.projects().builds().cancel(projectId=project, id=buildId)
        status, msg = Command._api_call(method)

        if status == "200":
            return "Build cancelled"
        elif status == "404":
            return "No build found in %s with ID %s" % (project, argv[0])

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

        # GCB BuildID field is 36 characters
        if len(buildId) < 36:
            return "Invalid build ID"

        method = cloudbuild.projects().builds().retry(projectId=project, id=buildId)
        status, msg = Command._api_call(method)

        if status == "200":
            return "Submitted retry request"
        elif status == "404":
            return "No build found in %s with ID %s" % (project, argv[0])

        print("Unhandled status : %s - %s" % (status, msg))
        return msg

    # TODO
    # @staticmethod
    # def trigger(argv: list, cloudbuild, project):

    #    return None

    @staticmethod
    def _api_call(method, include_resp=False):
        try:
            op = method.execute()

            if not include_resp:
                done = op.get("done", False)
                if done and op.get("error", {}) != {}:
                    return "0", op.get("error").get("message", "Unknown error")
            else:
                return "200", op
        except HttpError as err:
            if not include_resp:
                return str(err.resp.status), err._get_reason()

        return "200", ""
