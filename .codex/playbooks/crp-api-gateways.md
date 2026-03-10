# CRP API Gateways

Purpose: canonical API Gateway reference for the locally downloaded CRP frontend and lambdas.

- Region: `eu-west-1`
- Evidence scope:
  - Frontend hardcoded URLs in `cloud-repos-panel` service files
  - WebSocket endpoint usage in `cloud-repos-panel`
  - Local lambda code that targets the WebSocket management endpoint

## HTTP API used by cloud-repos-panel

### `mpq5pzhhv2`

- Execute API base URL: `https://mpq5pzhhv2.execute-api.eu-west-1.amazonaws.com`
- Observed stage: `prod`
- Consumer frontend:
  - `/Users/john/Downloads/projects/cloud-repos-panel/src/app/shared/data-storage.service.ts`
  - `/Users/john/Downloads/projects/cloud-repos-panel/src/app/shared/auth/auth.service.ts`
- Name resolution:
  - API name was not resolved from local IaC files in this workspace.
  - Until a generated AWS snapshot or IaC source is added, use the API ID itself as the normalized API token in refs.
- Normalized path convention for frontend refs:
  - `mpq5pzhhv2/prod/<route-or-lambda>`

Observed frontend routes on this API include:

- `test-connection`
- `crp-login`
- `crp-renew-token`
- `crp-fetch-admin-sockets`
- `crp-fetch-admins`
- `crp-handle-admin`
- `crp-handle-org`
- `crp-fetch-repos`
- `crp-search-repos`
- `crp-handle-repos-collaborators`
- `crp-handle-repos-invitations`
- `crp-create-repo`
- `crp-fetch-projects`
- `crp-search-projects`
- `crp-check-project-technical-data-ai`
- `crp-handle-project`
- `crp-fetch-subprojects`
- `crp-handle-subproject`
- `crp-search-subprojects`
- `crp-fetch-features`
- `crp-search-features`
- `crp-check-feature-technical-data-ai`
- `crp-handle-feature`
- `crp-fetch-cloud-repos`
- `crp-fetch-aws-resources-connections`
- `crp-create-comments-repo-code-ai`
- `crp-summarize-commits-repo-code-ai`
- `crp-check-repo-technical-data-ai`
- `crp-check-repo-code-ai`
- `crp-analyze-repo-code-ai`
- `crp-review-repo-code-ai`
- `crp-precheck-repo-code-technical-data-ai`
- `crp-upgrade-repo-code-ai`
- `crp-handle-readme-repo`
- `crp-handle-cloud-resource`
- `crp-fetch-cloud-resources`
- `crp-search-cloud-resources`
- `crp-handle-cloud-repo`
- `crp-handle-aws-resource`
- `crp-fetch-aws-resources`
- `crp-search-aws-resources`
- `crp-get-aws-resources-data`
- `crp-handle-aws-resources-data`
- `crp-handle-ai-job`
- `crp-fetch-prompts`
- `crp-handle-prompts`
- `crp-fetch-chats`
- `crp-handle-chat`
- `crp-fetch-ai-jobs`
- `crp-search-ai-jobs`
- `crp-fetch-fine-tuning-models`
- `crp-handle-fine-tuning-model`
- `crp-fetch-assistants`
- `crp-handle-assistant`
- `crp-fetch-vector-stores`
- `crp-handle-vector-store`
- `crp-fetch-openai-platform-files`
- `crp-handle-openai-platform-file`
- `crp-create-project-technical-data-files-async`
- `crp-fetch-db-openai-platform-store-files`

## WebSocket / Management API used by realtime flows

### `toswnx8m2d`

- WebSocket URL used by `cloud-repos-panel`:
  - `wss://toswnx8m2d.execute-api.eu-west-1.amazonaws.com/production/`
- Management endpoint used by `crp-socket-emitter-sqs`:
  - `https://toswnx8m2d.execute-api.eu-west-1.amazonaws.com/production`
- Observed stage: `production`
- Evidence:
  - `/Users/john/Downloads/projects/cloud-repos-panel/src/app/app.component.ts`
  - `/Users/john/Downloads/lambdas/crp_all/crp-socket-emitter-sqs/api_gateway_functions.js`
- Name resolution:
  - API name was not resolved from local IaC files in this workspace.
  - Keep the API ID in normalized references until an AWS snapshot or IaC mapping is added.
