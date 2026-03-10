# cloud-repos-panel frontend -> HTTP lambdas

Purpose: document HTTP lambdas called from the `cloud-repos-panel` frontend (`*.service.ts` only), with normalized paths and verified local mapping status.

## API Ids -> API names

- `mpq5pzhhv2` -> unresolved API name in local files; use API ID as normalized token

## Sources

- `/Users/john/Downloads/projects/cloud-repos-panel/src/app/shared/auth/auth.service.ts`
- `/Users/john/Downloads/projects/cloud-repos-panel/src/app/shared/data-storage.service.ts`

## Coverage summary

- Observed frontend HTTP routes: `60`
- HTTP method observed for all frontend calls in scope: `POST`
- Routes with local lambda folder present: `58`
- Routes without a matching local lambda folder:
  - `test-connection`
  - `crp-handle-ai-job`

## Contract notes

- Authentication routes have explicit response typings in the frontend:
  - `crp-login`
  - `crp-renew-token`
- Most non-auth routes are consumed through `handleRequest<T>()` and treated as:
  - `success: boolean`
  - optional `comment_id`
  - optional `data`
- The generated companion ref contains the per-route payload inventory:
  - `cloud-repos-panel-lambdas.generated.md`

## Verified route inventory

| Normalized | Route | Local lambda folder | Source |
| --- | --- | --- | --- |
| `mpq5pzhhv2/prod/test-connection` | `/test-connection` | `missing locally` | `data-storage.service.ts:77` |
| `mpq5pzhhv2/prod/crp-login` | `/crp-login` | `crp-login` | `auth.service.ts:54` |
| `mpq5pzhhv2/prod/crp-renew-token` | `/crp-renew-token` | `crp-renew-token` | `auth.service.ts:116` |
| `mpq5pzhhv2/prod/crp-fetch-admin-sockets` | `/crp-fetch-admin-sockets` | `crp-fetch-admin-sockets` | `data-storage.service.ts:196` |
| `mpq5pzhhv2/prod/crp-fetch-admins` | `/crp-fetch-admins` | `crp-fetch-admins` | `data-storage.service.ts:209` |
| `mpq5pzhhv2/prod/crp-handle-admin` | `/crp-handle-admin` | `crp-handle-admin` | `data-storage.service.ts:222` |
| `mpq5pzhhv2/prod/crp-handle-org` | `/crp-handle-org` | `crp-handle-org` | `data-storage.service.ts:241` |
| `mpq5pzhhv2/prod/crp-fetch-repos` | `/crp-fetch-repos` | `crp-fetch-repos` | `data-storage.service.ts:263` |
| `mpq5pzhhv2/prod/crp-search-repos` | `/crp-search-repos` | `crp-search-repos` | `data-storage.service.ts:284` |
| `mpq5pzhhv2/prod/crp-handle-repos-collaborators` | `/crp-handle-repos-collaborators` | `crp-handle-repos-collaborators` | `data-storage.service.ts:323` |
| `mpq5pzhhv2/prod/crp-handle-repos-invitations` | `/crp-handle-repos-invitations` | `crp-handle-repos-invitations` | `data-storage.service.ts:331` |
| `mpq5pzhhv2/prod/crp-create-repo` | `/crp-create-repo` | `crp-create-repo` | `data-storage.service.ts:339` |
| `mpq5pzhhv2/prod/crp-fetch-projects` | `/crp-fetch-projects` | `crp-fetch-projects` | `data-storage.service.ts:355` |
| `mpq5pzhhv2/prod/crp-search-projects` | `/crp-search-projects` | `crp-search-projects` | `data-storage.service.ts:383` |
| `mpq5pzhhv2/prod/crp-check-project-technical-data-ai` | `/crp-check-project-technical-data-ai` | `crp-check-project-technical-data-ai` | `data-storage.service.ts:404` |
| `mpq5pzhhv2/prod/crp-handle-project` | `/crp-handle-project` | `crp-handle-project` | `data-storage.service.ts:412` |
| `mpq5pzhhv2/prod/crp-fetch-subprojects` | `/crp-fetch-subprojects` | `crp-fetch-subprojects` | `data-storage.service.ts:428` |
| `mpq5pzhhv2/prod/crp-handle-subproject` | `/crp-handle-subproject` | `crp-handle-subproject` | `data-storage.service.ts:452` |
| `mpq5pzhhv2/prod/crp-search-subprojects` | `/crp-search-subprojects` | `crp-search-subprojects` | `data-storage.service.ts:468` |
| `mpq5pzhhv2/prod/crp-fetch-features` | `/crp-fetch-features` | `crp-fetch-features` | `data-storage.service.ts:494` |
| `mpq5pzhhv2/prod/crp-search-features` | `/crp-search-features` | `crp-search-features` | `data-storage.service.ts:535` |
| `mpq5pzhhv2/prod/crp-check-feature-technical-data-ai` | `/crp-check-feature-technical-data-ai` | `crp-check-feature-technical-data-ai` | `data-storage.service.ts:557` |
| `mpq5pzhhv2/prod/crp-handle-feature` | `/crp-handle-feature` | `crp-handle-feature` | `data-storage.service.ts:573` |
| `mpq5pzhhv2/prod/crp-fetch-cloud-repos` | `/crp-fetch-cloud-repos` | `crp-fetch-cloud-repos` | `data-storage.service.ts:603` |
| `mpq5pzhhv2/prod/crp-fetch-aws-resources-connections` | `/crp-fetch-aws-resources-connections` | `crp-fetch-aws-resources-connections` | `data-storage.service.ts:641` |
| `mpq5pzhhv2/prod/crp-create-comments-repo-code-ai` | `/crp-create-comments-repo-code-ai` | `crp-create-comments-repo-code-ai` | `data-storage.service.ts:680` |
| `mpq5pzhhv2/prod/crp-summarize-commits-repo-code-ai` | `/crp-summarize-commits-repo-code-ai` | `crp-summarize-commits-repo-code-ai` | `data-storage.service.ts:688` |
| `mpq5pzhhv2/prod/crp-check-repo-technical-data-ai` | `/crp-check-repo-technical-data-ai` | `crp-check-repo-technical-data-ai` | `data-storage.service.ts:698` |
| `mpq5pzhhv2/prod/crp-check-repo-code-ai` | `/crp-check-repo-code-ai` | `crp-check-repo-code-ai` | `data-storage.service.ts:706` |
| `mpq5pzhhv2/prod/crp-analyze-repo-code-ai` | `/crp-analyze-repo-code-ai` | `crp-analyze-repo-code-ai` | `data-storage.service.ts:714` |
| `mpq5pzhhv2/prod/crp-review-repo-code-ai` | `/crp-review-repo-code-ai` | `crp-review-repo-code-ai` | `data-storage.service.ts:722` |
| `mpq5pzhhv2/prod/crp-precheck-repo-code-technical-data-ai` | `/crp-precheck-repo-code-technical-data-ai` | `crp-precheck-repo-code-technical-data-ai` | `data-storage.service.ts:730` |
| `mpq5pzhhv2/prod/crp-upgrade-repo-code-ai` | `/crp-upgrade-repo-code-ai` | `crp-upgrade-repo-code-ai` | `data-storage.service.ts:764` |
| `mpq5pzhhv2/prod/crp-handle-readme-repo` | `/crp-handle-readme-repo` | `crp-handle-readme-repo` | `data-storage.service.ts:782` |
| `mpq5pzhhv2/prod/crp-handle-cloud-resource` | `/crp-handle-cloud-resource` | `crp-handle-cloud-resource` | `data-storage.service.ts:814` |
| `mpq5pzhhv2/prod/crp-fetch-cloud-resources` | `/crp-fetch-cloud-resources` | `crp-fetch-cloud-resources` | `data-storage.service.ts:846` |
| `mpq5pzhhv2/prod/crp-search-cloud-resources` | `/crp-search-cloud-resources` | `crp-search-cloud-resources` | `data-storage.service.ts:886` |
| `mpq5pzhhv2/prod/crp-handle-cloud-repo` | `/crp-handle-cloud-repo` | `crp-handle-cloud-repo` | `data-storage.service.ts:905` |
| `mpq5pzhhv2/prod/crp-handle-aws-resource` | `/crp-handle-aws-resource` | `crp-handle-aws-resource` | `data-storage.service.ts:942` |
| `mpq5pzhhv2/prod/crp-fetch-aws-resources` | `/crp-fetch-aws-resources` | `crp-fetch-aws-resources` | `data-storage.service.ts:964` |
| `mpq5pzhhv2/prod/crp-search-aws-resources` | `/crp-search-aws-resources` | `crp-search-aws-resources` | `data-storage.service.ts:1040` |
| `mpq5pzhhv2/prod/crp-get-aws-resources-data` | `/crp-get-aws-resources-data` | `crp-get-aws-resources-data` | `data-storage.service.ts:1058` |
| `mpq5pzhhv2/prod/crp-handle-aws-resources-data` | `/crp-handle-aws-resources-data` | `crp-handle-aws-resources-data` | `data-storage.service.ts:1078` |
| `mpq5pzhhv2/prod/crp-handle-ai-job` | `/crp-handle-ai-job` | `missing locally` | `data-storage.service.ts:1100` |
| `mpq5pzhhv2/prod/crp-fetch-prompts` | `/crp-fetch-prompts` | `crp-fetch-prompts` | `data-storage.service.ts:1129` |
| `mpq5pzhhv2/prod/crp-handle-prompts` | `/crp-handle-prompts` | `crp-handle-prompts` | `data-storage.service.ts:1137` |
| `mpq5pzhhv2/prod/crp-fetch-chats` | `/crp-fetch-chats` | `crp-fetch-chats` | `data-storage.service.ts:1146` |
| `mpq5pzhhv2/prod/crp-handle-chat` | `/crp-handle-chat` | `crp-handle-chat` | `data-storage.service.ts:1172` |
| `mpq5pzhhv2/prod/crp-fetch-ai-jobs` | `/crp-fetch-ai-jobs` | `crp-fetch-ai-jobs` | `data-storage.service.ts:1195` |
| `mpq5pzhhv2/prod/crp-search-ai-jobs` | `/crp-search-ai-jobs` | `crp-search-ai-jobs` | `data-storage.service.ts:1216` |
| `mpq5pzhhv2/prod/crp-fetch-fine-tuning-models` | `/crp-fetch-fine-tuning-models` | `crp-fetch-fine-tuning-models` | `data-storage.service.ts:1236` |
| `mpq5pzhhv2/prod/crp-handle-fine-tuning-model` | `/crp-handle-fine-tuning-model` | `crp-handle-fine-tuning-model` | `data-storage.service.ts:1261` |
| `mpq5pzhhv2/prod/crp-fetch-assistants` | `/crp-fetch-assistants` | `crp-fetch-assistants` | `data-storage.service.ts:1281` |
| `mpq5pzhhv2/prod/crp-handle-assistant` | `/crp-handle-assistant` | `crp-handle-assistant` | `data-storage.service.ts:1296` |
| `mpq5pzhhv2/prod/crp-fetch-vector-stores` | `/crp-fetch-vector-stores` | `crp-fetch-vector-stores` | `data-storage.service.ts:1316` |
| `mpq5pzhhv2/prod/crp-handle-vector-store` | `/crp-handle-vector-store` | `crp-handle-vector-store` | `data-storage.service.ts:1331` |
| `mpq5pzhhv2/prod/crp-fetch-openai-platform-files` | `/crp-fetch-openai-platform-files` | `crp-fetch-openai-platform-files` | `data-storage.service.ts:1347` |
| `mpq5pzhhv2/prod/crp-handle-openai-platform-file` | `/crp-handle-openai-platform-file` | `crp-handle-openai-platform-file` | `data-storage.service.ts:1362` |
| `mpq5pzhhv2/prod/crp-create-project-technical-data-files-async` | `/crp-create-project-technical-data-files-async` | `crp-create-project-technical-data-files-async` | `data-storage.service.ts:1377` |
| `mpq5pzhhv2/prod/crp-fetch-db-openai-platform-store-files` | `/crp-fetch-db-openai-platform-store-files` | `crp-fetch-db-openai-platform-store-files` | `data-storage.service.ts:1392` |
