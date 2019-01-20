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
   * `python test_render.py failed.json`
   * ```
     {
         "text" : "12345678 failed!" 
     }
     ```
   * paste the contents into Slack's [message builder](https://api.slack.com/docs/messages/builder) for a preview

## Provided template variables

* `${build_color}` - Hex value of color matching the build status (red for failure, green for success, etc)
* `${build_id}` - the cloud build id for this message
* `${build_id_short}` - the first eight characters of the cloud build id
* `${build_log_url}` - URL to the logs for this cloud build
* `${build_status}` - the current status for this cloud build
* `${project_id}` - GCP Project ID where cloud build is running

`token` and `channel` are supplied at runtime, so don't include it in the template file.

