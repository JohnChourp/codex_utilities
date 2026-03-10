# CRP S3 Buckets

Purpose: canonical S3 resource notes derived from locally downloaded CRP lambda code and README files.

- Region observed in code: `eu-west-1`

## `cloud-repos-panel-data`

Observed usage:

- `crp-handle-cloud-resource`
  - Uploads, reads, and deletes JSON technical data.
  - Evidence:
    - `/Users/john/Downloads/lambdas/crp_all/crp-handle-cloud-resource/s3_functions.js`
    - `/Users/john/Downloads/lambdas/crp_all/crp-handle-cloud-resource/README.md`
- `crp-check-repo-technical-data-ai`
  - Reads existing repo technical data and writes updated outputs/prompts.
  - Evidence:
    - `/Users/john/Downloads/lambdas/crp_all/crp-check-repo-technical-data-ai/s3_functions.js`
    - `/Users/john/Downloads/lambdas/crp_all/crp-check-repo-technical-data-ai/README.md`
- `crp-upgrade-repo-code-ai`
  - Reads repo-side technical artifacts and prompt metadata.
  - Evidence:
    - `/Users/john/Downloads/lambdas/crp_all/crp-upgrade-repo-code-ai/s3_functions.js`
    - `/Users/john/Downloads/lambdas/crp_all/crp-upgrade-repo-code-ai/README.md`

Data shape observed:

- JSON technical-data files for repos/cloud resources.
- Prompt-related JSON payloads consumed by AI-analysis flows.

## `openai-platform-store`

Observed usage:

- `crp-openai-platform-store-stream`
  - Trigger source for `ObjectCreated` PDF uploads.
  - Downloads PDF files from S3, generates OpenAI-driven analysis, then stores JSON output back to S3 when size allows.
  - Evidence:
    - `/Users/john/Downloads/lambdas/crp_all/crp-openai-platform-store-stream/s3_functions.js`
    - `/Users/john/Downloads/lambdas/crp_all/crp-openai-platform-store-stream/README.md`

Data shape observed:

- Incoming PDF files.
- Derived JSON technical-analysis artifacts.
