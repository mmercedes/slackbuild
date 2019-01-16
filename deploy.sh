#!/bin/bash

deps=("gcloud" "gsutil" "jq")

for dep in "${deps[@]}"; do
    command -v "$dep" 1>/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Dependency '$dep' not found in PATH. Exiting"
        exit 1
    fi
done

set -e

PROJECT_ID=$(jq -r .gcloud.project_id < config.json)
BUCKET_URL=$(jq -r .gcloud.gcs_bucket_url < config.json)

# log commands from this point onward
set -x

gsutil ls "$BUCKET_URL" 1>/dev/null || gsutil mb -p "$PROJECT_ID" "$BUCKET_URL"

gcloud beta functions deploy slackbuild-pubsub \
    --runtime python37 \
    --trigger-topic cloud-builds \
    --entry-point slackbuild_pubsub \
    --source=. \
    --stage-bucket="$BUCKET_URL" \
    --env-vars-file=env.yaml \
    --project "$PROJECT_ID"

#gcloud beta functions deploy slackbuild-webhook \
#    --runtime python37 \
#    --trigger-http \
#    --entry-point slackbuild_webhook \
#    --source=. \
#    --stage-bucket="$BUCKET_URL" \
#    --env-vars-file=env.yaml \
#    --project "$PROJECT_ID"
