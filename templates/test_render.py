import json
import os
import sys

sys.path.append("..")
from slackbuild.slack import Slack

if len(sys.argv) < 2 :
    print('usage: python test_render.py [template file]')
    exit(1)

template = sys.argv[1]

variables = {
    "build_color": "#32cd32",
    "build_id": "12345678-9012345-123425",
    "build_id_short": "12345678",
    "build_log_url": "http://google.com",
    "build_status": "Success",
    "build_duration": "3 seconds",

    "repo_name": "testrepo",
    "revision": "ab12cd34ef560a123",
    "revision_sha_short": "ab12cd34",
    "revision_url": "github.com/you/testrepo/commits/ab12cd34ef560a123",

    "project_id": "my-project"
}

s = Slack({})
output = s.render_message(variables, template)
print(json.dumps(output, sort_keys=True, indent=4))
