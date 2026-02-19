#!/usr/bin/env bash

## This script was auto-generated to clone the selected repositories.
## Keep it secret – it contains your GitHub token.
## Place this script in the folder where you want the repos to live and run it there.

# Default concurrency (override via env: CONCURRENCY=20 ./clone_selected_repos.sh)
CONCURRENCY="${CONCURRENCY:-10}"

githubHost="github.com"
GITHUB_TOKEN="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"

if [ -z "$GITHUB_TOKEN" ]; then
  echo "⛔ GITHUB_TOKEN is empty. Edit this script and set it to a valid GitHub token."
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
cd "$script_dir" || exit 1

echo "⚙️ Using concurrency: ${CONCURRENCY}"

repos=(
  "crp-repos-sqs-trigger"
  "crp-cli"
  "crp-search-repos"
  "crp-handle-feature"
  "crp-search-features"
  "crp-fetch-ai-jobs"
  "crp-precheck-repo-code-technical-data-ai"
  "crp-create-project-technical-data-files"
  "crp-fetch-openai-platform-files"
  "crp-search-projects"
  "crp-organizations-stream-ws"
  "crp-check-feature-technical-data-ai"
  "crp-handle-chat"
  "crp-handle-project"
  "crp-init-cloud-resources-attribute-values-json"
  "crp-search-ai-jobs"
  "crp-fetch-vector-stores"
  "crp-check-repo-code-ai"
  "crp-handle-prompts"
  "crp-handle-repo-collaborator"
  "crp-update-aws-connections-stream"
  "crp-projects-handle-features-stream"
  "crp-handle-org"
  "crp-handle-aws-resources-data"
  "crp-fetch-prompts-previous-versions"
  "crp-features-handle-cloud-repos-stream"
  "crp-fetch-repo-invitations"
  "crp-handle-admin"
  "crp-init-kinesis-aws-data"
  "crp-review-repo-code-ai"
  "crp-fetch-subprojects"
  "crp-handle-repos-collaborators"
  "crp-fetch-cloud-repos"
  "crp-handle-readme-repo"
  "crp-handle-aws-resource"
  "crp-fetch-repos"
  "crp-projects-stream-ws"
  "crp-get-response-ai"
  "crp-socket-emitter-sqs"
  "crp-init-s3-aws-data"
  "crp-fetch-fine-tuning-models"
  "crp-fetch-cloud-resources"
  "crp-fetch-prompts-previous-version"
  "crp-sockets-steam"
  "crp-create-repo"
  "crp-init-log-groups-aws-data"
  "crp-handle-subproject"
  "crp-check-project-technical-data-ai"
  "crp-init-event-bridge-aws-data"
  "crp-aws-resources-connections-stream-ws"
  "crp-fetch-projects"
  "crp-fetch-chats"
  "crp-repos-stream-ws"
  "crp-fetch-features"
  "crp-init-sns-aws-data"
  "crp-fetch-aws-resources"
  "crp-check-latest-updated-repos"
  "crp-features-stream-ws"
  "crp-init-lambda-cloud-resources"
  "crp-users-stream-ws"
  "crp-handle-prompts-previous-version"
  "crp-ws-connect"
  "crp-search-aws-resources"
  "crp-fetch-chat"
  "crp-fetch-db-openai-platform-store-files"
  "crp-handle-repos-invitations"
  "crp-ai-jobs-stream"
  "crp-create-comments-repo-code-ai"
  "crp-handle-cloud-repo"
  "crp-ws-cloud-command-response"
  "crp-init-repos-json"
  "crp-cloud-resources-stream-ws"
  "crp-init-api-gateway-aws-data"
  "crp-fetch-admins"
  "crp-handle-openai-platform-file"
  "crp-search-cloud-resources"
  "crp-init-dynamo-db-aws-data"
  "crp-lambda-events-trigger"
  "crp-login"
  "crp-handle-vector-store"
  "crp-renew-token"
  "crp-ws-disconnect"
  "crp-analyze-repo-code-ai"
  "crp-fetch-prompts"
  "crp-init-repos-aws-data"
  "crp-create-project-technical-data-files-async"
  "crp-summarize-commits-repo-code-ai"
  "crp-upgrade-repo-code-ai"
  "crp-openai-platform-store-stream"
  "crp-fetch-admin-sockets"
  "crp-handle-assistant"
  "crp-fetch-aws-resources-connections"
  "crp-subprojects-stream-ws"
  "crp-search-subprojects"
  "crp-search-cloud-repos"
  "crp-fetch-assistants"
  "crp-check-repo-technical-data-ai"
  "crp-init-sqs-aws-data"
  "crp-handle-fine-tuning-model"
  "crp-handle-cloud-resource"
  "crp-authorizer"
  "crp-routes-paths-calculations-stream-update-routes-paths"
  "crp-get-aws-resources-data"
  "crp-handle-github-webhook"
  "crp-lambda-aws-resources-stream-ws"
  "-crp-subprojects-stream-ws"
  "crp-aws-resources-stream-ws"
  "crp-subprojects-handle-features-stream"
  "crp-aws-resource-connections"
)

clone_repo() {
  local fullName="$1"
  local repoDir="${fullName##*/}"

  if [ -d "$repoDir/.git" ]; then
    echo "✅ Skipping ${fullName}: already cloned in ${repoDir}"
    return 0
  fi
  if [ -d "$repoDir" ]; then
    echo "⚠️ Skipping ${fullName}: directory ${repoDir} exists but is not a git repo."
    return 0
  fi

  echo "🌀 Cloning ${fullName} ..."
  if git clone "https://${GITHUB_TOKEN}@${githubHost}/dmngr/${fullName}.git"; then
    echo "✅ Done ${fullName}"
  else
    echo "⛔ Failed ${fullName}" >&2
    return 1
  fi
}

export -f clone_repo
export githubHost
export GITHUB_TOKEN

printf "%s\0" "${repos[@]}" | xargs -0 -n 1 -P "$CONCURRENCY" -I {} bash -c 'clone_repo "$1"' _ {}

echo "All done!"