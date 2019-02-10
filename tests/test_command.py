import json
import unittest
from slackbuild.config import Config
from slackbuild.command import Command
from googleapiclient.errors import HttpError


class TestCommand(unittest.TestCase):

    config_override = {
        "gcloud": {
            "project_id": "myproject"
        }
    }

    def test_parse(self):
        cases = [
            ("retry e36544dc-82a1-cc63-bac7-a6b2d18d7ea6", ["retry", "e36544dc-82a1-cc63-bac7-a6b2d18d7ea6"]),
            ("   ", []),
            (" a b  c ", ["a", "b", "c"])
        ]

        actual = Command.parse({})

        self.assertEqual([], actual)

        for case in cases:
            text, expected = case
            input = {"text": text}
            actual = Command.parse(input)
            self.assertEqual(expected, actual)

    def test_run_bad_input(self):
        actual = Command.run({"text": "foo"}, None, self.config_override)
        self.assertEqual({"result": Command.BAD_INPUT}, actual)

        actual = Command.run({}, None, self.config_override)
        self.assertEqual({"result": Command.BAD_INPUT}, actual)

        actual = Command.run({"text": "retry"}, None, self.config_override)
        self.assertEqual({"result": "Usage: retry <buildId>"}, actual)

        actual = Command.run({"text": "cancel"}, None, self.config_override)
        self.assertEqual({"result": "Usage: cancel <buildId>"}, actual)

    def test_run_success(self):
        f = open('mocks/webhook/form.json')
        data = json.load(f)
        f.close()

        f = open('mocks/webhook/operation.json')
        op = json.load(f)
        f.close()

        # test for successful retry command
        cloudbuild = Mock_CloudBuild('cloudbuild.projects.builds.retry.execute',
                                     {'projectId': 'myproject', 'id': '12345678-9012-3456-7890-123456789012'},
                                     op)
        actual = Command.run(data, cloudbuild, self.config_override)
        self.assertEqual({"result": "Submitted retry request"}, actual)

        # test for successful cancel command
        data["text"] = "cancel 12345678-9012-3456-7890-123456789012"
        cloudbuild = Mock_CloudBuild('cloudbuild.projects.builds.cancel.execute',
                                     {'projectId': 'myproject', 'id': '12345678-9012-3456-7890-123456789012'},
                                     op)
        actual = Command.run(data, cloudbuild, self.config_override)
        self.assertEqual({"result": "Build cancelled"}, actual)

    def test_run_error(self):
        f = open('mocks/webhook/form.json')
        data = json.load(f)
        f.close()

        # https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.errors-pysrc.html
        err = HttpError(Mock_Response("404", "Entity not found"), b'', "https://cloudbuild.googleapis.com/v1/projects/myproject/builds/1234:retry")

        # test retry when client 404s
        cloudbuild = Mock_CloudBuild('cloudbuild.projects.builds.retry.execute',
                                     {'projectId': 'myproject', 'id': '12345678-9012-3456-7890-123456789012'},
                                     None, error=err)
        actual = Command.run(data, cloudbuild, self.config_override)
        self.assertEqual({"result": "No build found in myproject with ID 12345678-9012-3456-7890-123456789012"}, actual)

        # test cancel when client 404s
        data["text"] = "cancel 12345678-9012-3456-7890-123456789012"
        cloudbuild = Mock_CloudBuild('cloudbuild.projects.builds.cancel.execute',
                                     {'projectId': 'myproject', 'id': '12345678-9012-3456-7890-123456789012'},
                                     None, error=err)
        actual = Command.run(data, cloudbuild, self.config_override)
        self.assertEqual({"result": "No build found in myproject with ID 12345678-9012-3456-7890-123456789012"}, actual)

        err = HttpError(Mock_Response("500", "Server error"), b'', "https://cloudbuild.googleapis.com/v1/projects/myproject/builds/1234:retry")

        # test retry when client 500s
        cloudbuild = Mock_CloudBuild('cloudbuild.projects.builds.retry.execute',
                                     {'projectId': 'myproject', 'id': '12345678-9012-3456-7890-123456789012'},
                                     None, error=err)
        actual = Command.run(data, cloudbuild, self.config_override)
        self.assertEqual({"result": "Server error"}, actual)

        # test cancel when client 500s
        data["text"] = "cancel 12345678-9012-3456-7890-123456789012"
        cloudbuild = Mock_CloudBuild('cloudbuild.projects.builds.cancel.execute',
                                     {'projectId': 'myproject', 'id': '12345678-9012-3456-7890-123456789012'},
                                     None, error=err)
        actual = Command.run(data, cloudbuild, self.config_override)
        self.assertEqual({"result": "Server error"}, actual)


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
