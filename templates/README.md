## What are message templates?

Slackbuild templates are json files representing an instance of the arguments to the `chat.postMessage` [slack API endpoint](https://api.slack.com/methods/chat.postMessage). View Slack's [message builder](https://api.slack.com/docs/messages/builder) for examples of what is possible.

You can provide a default template for all messages, or use a template for only certain [build statuses](https://cloud.google.com/cloud-build/docs/api/reference/rest/v1/projects.builds#Build.Status). 

## Creating a new message template

1. Add a new json file in the `templates/` directory
   * `touch templates/failed.json`
   * ```
     {
         "text" : "${build_id} failed!" 
     }
     ```

2. Add a config entry
   * `cat config.yaml`
   * ```
     slack:
       templates:
         failed: failed.json
     ...
     ```
3. Test your template
   * `cd templates && python test_render.py failed.json`
   * ```
     {
         "text" : "12345678 failed!" 
     }
     ```
   * paste the contents into Slack's [message builder](https://api.slack.com/docs/messages/builder) for a preview

## Provided template variables

* `${build_color}`
  - Hex value of color matching the build status (red for failure, green for success, etc)
* `${build_id}`
  - the cloud build id for this message
* `${build_id_short}`
  - the first eight characters of the cloud build id
* `${build_log_url}`
  - URL to the logs for this cloud build
* `${build_status}`
  - the current status for this cloud build
* `${repo_name}`
  - name of the source respository. Only set if source repo is provided, such as when the build is kicked off via a trigger, or if the substitution `_REPO` is present
* `${revision}`
  - Set to either commit sha or branch name. If build is not kicked off via a trigger, then will attempt to use of the value of the `_GIT_SHA` or `_BRANCH` substitution. See [Cloud Build docs](https://cloud.google.com/cloud-build/docs/api/reference/rest/v1/RepoSource) for more info.
* `${revision_sha_short}`
  - if revision is a git sha, this will be the first 8 characters, otherwise it will equal revision
* `${revision_url}`
  - Link to the revision that kicked off the build. If not using Google Cloud Source repos, set `github_url` in your config.yaml for this to be generated.
* `${project_id}`
  - GCP Project ID where cloud build is running

`token` and `channel` are supplied at runtime, so don't include it in the template file.

