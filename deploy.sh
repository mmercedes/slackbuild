#!/bin/bash

source secrets.sh

set -x
set -e

gsutil ls $BUCKET_URL 1>/dev/null || gsutil mb -p $PROJECT_ID $BUCKET_URL

gcloud beta functions deploy slackbuild-pubsub \
    --runtime python37 \
    --trigger-topic cloud-builds \
    --entry-point slackbuild_pubsub \
    --source=. \
    --stage-bucket=$BUCKET_URL \
    --env-vars-file=env.yaml \
    --project $PROJECT_ID

