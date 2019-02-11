import json
import unittest
from slackbuild.config import Config
from slackbuild.command import Command
from slackbuild.slack import Slack
from googleapiclient.errors import HttpError


class TestCommand(unittest.TestCase):

    config_override = {
        "gcloud": {
            "project_id": "myproject"
        }
    }

    def test_run_bad_input(self):
        actual, success = Command.run(["foo"], None, self.config_override)
        self.assertFalse(success)
        self.assertEqual(Command.BAD_INPUT, actual)

        actual, success = Command.run([], None, self.config_override)
        self.assertFalse(success)
        self.assertEqual(Command.BAD_INPUT, actual)

        actual, success = Command.run(["retry"], None, self.config_override)
        self.assertFalse(success)
        self.assertEqual("Usage: retry <buildId>", actual)

        actual, success = Command.run(["cancel"], None, self.config_override)
        self.assertFalse(success)
        self.assertEqual("Usage: cancel <buildId>", actual)

    def test_run_success(self):
        f = open('mocks/webhook/form.json')
        argv = Slack.parse_command(json.load(f))
        f.close()

        f = open('mocks/webhook/operation.json')
        op = json.load(f)
        f.close()

        # test for successful retry command
        cloudbuild = Mock_CloudBuild('cloudbuild.projects.builds.retry.execute',
                                     {'projectId': 'myproject', 'id': '12345678-9012-3456-7890-123456789012'},
                                     op)
        actual, success = Command.run(argv, cloudbuild, self.config_override)
        self.assertTrue(success)
        self.assertEqual("submitted retry request", actual)

        # test for successful cancel command
        argv = ["cancel", "12345678-9012-3456-7890-123456789012"]
        cloudbuild = Mock_CloudBuild('cloudbuild.projects.builds.cancel.execute',
                                     {'projectId': 'myproject', 'id': '12345678-9012-3456-7890-123456789012'},
                                     op)
        actual, success = Command.run(argv, cloudbuild, self.config_override)
        self.assertTrue(success)
        self.assertEqual("cancelled build", actual)

    def test_run_error(self):
        f = open('mocks/webhook/form.json')
        argv = Slack.parse_command(json.load(f))
        f.close()

        # https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.errors-pysrc.html
        err = HttpError(Mock_Response("404", "Entity not found"), b'', "https://cloudbuild.googleapis.com/v1/projects/myproject/builds/1234:retry")

        # test retry when client 404s
        cloudbuild = Mock_CloudBuild('cloudbuild.projects.builds.retry.execute',
                                     {'projectId': 'myproject', 'id': '12345678-9012-3456-7890-123456789012'},
                                     None, error=err)
        actual, success = Command.run(argv, cloudbuild, self.config_override)
        self.assertFalse(success)
        self.assertEqual("No build found in myproject with ID 12345678-9012-3456-7890-123456789012", actual)

        # test cancel when client 404s
        cloudbuild = Mock_CloudBuild('cloudbuild.projects.builds.cancel.execute',
                                     {'projectId': 'myproject', 'id': '12345678-9012-3456-7890-123456789012'},
                                     None, error=err)
        actual, success = Command.run(["cancel", "12345678-9012-3456-7890-123456789012"], cloudbuild, self.config_override)
        self.assertFalse(success)
        self.assertEqual("No build found in myproject with ID 12345678-9012-3456-7890-123456789012", actual)

        err = HttpError(Mock_Response("500", "Server error"), b'', "https://cloudbuild.googleapis.com/v1/projects/myproject/builds/1234:retry")

        # test retry when client 500s
        cloudbuild = Mock_CloudBuild('cloudbuild.projects.builds.retry.execute',
                                     {'projectId': 'myproject', 'id': '12345678-9012-3456-7890-123456789012'},
                                     None, error=err)
        actual, success = Command.run(argv, cloudbuild, self.config_override)
        self.assertFalse(success)
        self.assertEqual("Server error", actual)

        # test cancel when client 500s
        cloudbuild = Mock_CloudBuild('cloudbuild.projects.builds.cancel.execute',
                                     {'projectId': 'myproject', 'id': '12345678-9012-3456-7890-123456789012'},
                                     None, error=err)
        actual, success = Command.run(["cancel", "12345678-9012-3456-7890-123456789012"], cloudbuild, self.config_override)
        self.assertFalse(success)
        self.assertEqual("Server error", actual)


class Mock_CloudBuild():

    def __init__(self, method, kwargs, return_val, error=None):
        # method is of the form:
        # cloudbuild.foo.bar.execute
        # cloudbuild.foo.bar.baz.execute
        assert len(method.split('.')) > 1

        self.props = method.split('.')
        self.props.pop(0)  # remove 'cloudbuild.'
        self.leaf_method = self.props[-2]
        self.root_method = self.props[0]
        self.kwargs = kwargs
        self.return_val = return_val
        self.error = error

    def __getattr__(self, attr):
        return self

    def __call__(self, **kwargs):
        method = self.props.pop(0)

        if method == self.leaf_method:
            assert self.kwargs == kwargs

        if len(self.props) == 0:
            if self.error is not None:
                raise self.error
            return self.return_val

        return self


class Mock_Response():

    def __init__(self, status, reason):
        self.status = status
        self.reason = reason
