# slackbuild
Google [Cloud Build](https://cloud.google.com/cloud-build/) integration for Slack

![slack notifications from cloud build](slackbuild.png)

[![Build Status](https://travis-ci.org/mmercedes/slackbuild.svg?branch=master)](https://travis-ci.org/mmercedes/slackbuild)

### Install

- Clone this repo
- Create a new incoming webhook for Slack.  [Instructions](https://api.slack.com/incoming-webhooks)
- Add your slack token to `env.yaml`.  [Example](./env.example.yaml)
  * token is in a seperate file so you can commit your `config.yaml` without exposing the token
- Create a `config.yaml` file.  [Commented Example](./config.example.yaml)
```yaml
slack:
  channel: '#test'
gcloud:
  project_id: 'my-project'
  gcs_bucket_url: 'gs://my-bucket'
```
- Run `./deploy.sh`
  * this assumes you have the [gcloud sdk](https://cloud.google.com/sdk/install) installed and permission to create cloud functions and gcs buckets
  * This skips the tests. Run `make deploy` if you'd like to run the tests. (Assumes you have python 3.7 installed)

### TODO

- Support for custom message templates
- Example terraform config to avoid manual creation of cloud funcion
- Outgoing webhook mode to support Slack 'slash commands'
  * ex `/cloudbuilds <buildId> cancel`
- Standalone mode. Running with no cloud function creation
