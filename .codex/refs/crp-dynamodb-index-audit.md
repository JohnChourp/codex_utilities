# CRP DynamoDB index audit

- Root: `/home/dm-soft-1/Downloads/lambdas/crp_all`
- Mode: `live`
- Account ID: `957873067375`
- Profile: `active AWS CLI profile`
- Region: `active AWS CLI region`
- Scanned lambdas: `105`
- Scanned JS files: `449`
- Unique tables: `13`
- Resolved table/index pairs: `34`
- Confirmed present: `0`
- Missing in DynamoDB: `4`
- Unresolved needs manual review: `1`
- Table errors: `11`

## Confirmed present
- None

## Missing in DynamoDB
- `crp-lambda-aws-resources -> org-res_type_res_name-index`
  - `crp-search-aws-resources/dynamo_db_functions.js:37` (crp-search-aws-resources)
  - `crp-search-cloud-resources/dynamo_db_functions.js:41` (crp-search-cloud-resources)
  - `crp-search-cloud-resources/dynamo_db_functions.js:97` (crp-search-cloud-resources)
- `crp-lambda-aws-resources -> res_type-res_name-index`
  - `crp-fetch-cloud-resources/dynamo_db_functions.js:61` (crp-fetch-cloud-resources)
  - `crp-fetch-cloud-resources/dynamo_db_functions.js:87` (crp-fetch-cloud-resources)
  - `crp-search-cloud-resources/dynamo_db_functions.js:70` (crp-search-cloud-resources)
- `crp-subprojects -> org-subproject_name-index`
  - `crp-search-subprojects/dynamo_db_functions.js:36` (crp-search-subprojects)
- `crp-subprojects -> org-updated_timestamp-index`
  - `crp-fetch-subprojects/dynamo_db_functions.js:34` (crp-fetch-subprojects)

## Unresolved needs manual review
- `crp-update-aws-connections-stream/dynamo_db_functions.js:48` `table="crp-aws-resources-connections"` `index=indexName`
  - Reason: `dynamic expression: indexMap[resourceAKey]`

## Table errors
- `crp-ai-jobs`
  - Error: `aws: [ERROR]: An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: Requested resource not found: Table: crp-ai-jobs not found

Additional error details:
message: Requested resource not found: Table: crp-ai-jobs not found`
- `crp-aws-resources`
  - Error: `aws: [ERROR]: An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: Requested resource not found: Table: crp-aws-resources not found

Additional error details:
message: Requested resource not found: Table: crp-aws-resources not found`
- `crp-aws-resources-connections`
  - Error: `aws: [ERROR]: An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: Requested resource not found: Table: crp-aws-resources-connections not found

Additional error details:
message: Requested resource not found: Table: crp-aws-resources-connections not found`
- `crp-chats`
  - Error: `aws: [ERROR]: An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: Requested resource not found: Table: crp-chats not found

Additional error details:
message: Requested resource not found: Table: crp-chats not found`
- `crp-cloud-repos`
  - Error: `aws: [ERROR]: An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: Requested resource not found: Table: crp-cloud-repos not found

Additional error details:
message: Requested resource not found: Table: crp-cloud-repos not found`
- `crp-features`
  - Error: `aws: [ERROR]: An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: Requested resource not found: Table: crp-features not found

Additional error details:
message: Requested resource not found: Table: crp-features not found`
- `crp-fine-tuning-models`
  - Error: `aws: [ERROR]: An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: Requested resource not found: Table: crp-fine-tuning-models not found

Additional error details:
message: Requested resource not found: Table: crp-fine-tuning-models not found`
- `crp-openai-platform-store-files`
  - Error: `aws: [ERROR]: An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: Requested resource not found: Table: crp-openai-platform-store-files not found

Additional error details:
message: Requested resource not found: Table: crp-openai-platform-store-files not found`
- `crp-projects`
  - Error: `aws: [ERROR]: An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: Requested resource not found: Table: crp-projects not found

Additional error details:
message: Requested resource not found: Table: crp-projects not found`
- `crp-sockets`
  - Error: `aws: [ERROR]: An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: Requested resource not found: Table: crp-sockets not found

Additional error details:
message: Requested resource not found: Table: crp-sockets not found`
- `crp-users`
  - Error: `aws: [ERROR]: An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: Requested resource not found: Table: crp-users not found

Additional error details:
message: Requested resource not found: Table: crp-users not found`

## Resolved table/index pairs
- `crp-ai-jobs -> org-created_timestamp-index`
  - `crp-fetch-ai-jobs/dynamo_db_functions.js:34` (crp-fetch-ai-jobs)
  - `crp-fetch-ai-jobs/dynamo_db_functions.js:164` (crp-fetch-ai-jobs)
- `crp-ai-jobs -> org-job_type-index`
  - `crp-fetch-ai-jobs/dynamo_db_functions.js:99` (crp-fetch-ai-jobs)
- `crp-ai-jobs -> org-pusher_name-index`
  - `crp-fetch-ai-jobs/dynamo_db_functions.js:129` (crp-fetch-ai-jobs)
- `crp-ai-jobs -> org-repo_id-index`
  - `crp-fetch-ai-jobs/dynamo_db_functions.js:69` (crp-fetch-ai-jobs)
  - `crp-search-ai-jobs/dynamo_db_functions.js:34` (crp-search-ai-jobs)
  - `crp-search-ai-jobs/dynamo_db_functions.js:74` (crp-search-ai-jobs)
  - `crp-search-ai-jobs/dynamo_db_functions.js:138` (crp-search-ai-jobs)
- `crp-aws-resources -> org_res_type-resources_updated_at-index`
  - `crp-init-lambda-cloud-resources/dynamo_db_functions.js:34` (crp-init-lambda-cloud-resources)
- `crp-aws-resources-connections -> apigateway-connection_id-index`
  - `crp-fetch-aws-resources-connections/dynamo_db_functions.js:79` (crp-fetch-aws-resources-connections)
- `crp-aws-resources-connections -> dynamodb-connection_id-index`
  - `crp-fetch-aws-resources-connections/dynamo_db_functions.js:108` (crp-fetch-aws-resources-connections)
- `crp-aws-resources-connections -> eventbridge-connection_id-index`
  - `crp-fetch-aws-resources-connections/dynamo_db_functions.js:136` (crp-fetch-aws-resources-connections)
- `crp-aws-resources-connections -> glue-connection_id-index`
  - `crp-fetch-aws-resources-connections/dynamo_db_functions.js:164` (crp-fetch-aws-resources-connections)
- `crp-aws-resources-connections -> kinesis-connection_id-index`
  - `crp-fetch-aws-resources-connections/dynamo_db_functions.js:192` (crp-fetch-aws-resources-connections)
- `crp-aws-resources-connections -> lambda-connection_id-index`
  - `crp-fetch-aws-resources-connections/dynamo_db_functions.js:220` (crp-fetch-aws-resources-connections)
- `crp-aws-resources-connections -> loggroups-connection_id-index`
  - `crp-fetch-aws-resources-connections/dynamo_db_functions.js:248` (crp-fetch-aws-resources-connections)
- `crp-aws-resources-connections -> s3-connection_id-index`
  - `crp-fetch-aws-resources-connections/dynamo_db_functions.js:276` (crp-fetch-aws-resources-connections)
- `crp-aws-resources-connections -> sns-connection_id-index`
  - `crp-fetch-aws-resources-connections/dynamo_db_functions.js:304` (crp-fetch-aws-resources-connections)
- `crp-aws-resources-connections -> sqs-connection_id-index`
  - `crp-fetch-aws-resources-connections/dynamo_db_functions.js:332` (crp-fetch-aws-resources-connections)
- `crp-aws-resources-connections -> stepfunctions-connection_id-index`
  - `crp-fetch-aws-resources-connections/dynamo_db_functions.js:360` (crp-fetch-aws-resources-connections)
- `crp-chats -> org-chat_name-index`
  - `crp-fetch-chats/dynamo_db_functions.js:64` (crp-fetch-chats)
- `crp-cloud-repos -> org-repo_id-index`
  - `crp-check-repo-technical-data-ai/dynamo_db_functions.js:38` (crp-check-repo-technical-data-ai)
  - `crp-create-comments-repo-code-ai/dynamo_db_functions.js:172` (crp-create-comments-repo-code-ai)
  - `crp-fetch-cloud-repos/dynamo_db_functions.js:72` (crp-fetch-cloud-repos)
  - `crp-fetch-cloud-resources/dynamo_db_functions.js:115` (crp-fetch-cloud-resources)
  - `crp-fetch-features/dynamo_db_functions.js:144` (crp-fetch-features)
- `crp-cloud-repos -> project_id-repo_id-index`
  - `crp-fetch-cloud-repos/dynamo_db_functions.js:37` (crp-fetch-cloud-repos)
- `crp-features -> org-feature_id-index`
  - `crp-fetch-cloud-resources/dynamo_db_functions.js:137` (crp-fetch-cloud-resources)
  - `crp-fetch-features/dynamo_db_functions.js:37` (crp-fetch-features)
  - `crp-fetch-features/dynamo_db_functions.js:119` (crp-fetch-features)
  - `crp-search-repos/dynamo_db_functions.js:81` (crp-search-repos)
- `crp-features -> org-feature_name-index`
  - `crp-handle-cloud-repo/dynamo_db_functions.js:151` (crp-handle-cloud-repo)
  - `crp-search-features/dynamo_db_functions.js:33` (crp-search-features)
- `crp-features -> org-last_checked-index`
  - `crp-check-latest-updated-repos/dynamo_db_functions.js:104` (crp-check-latest-updated-repos)
- `crp-features -> project_id-filename-index`
  - `crp-handle-chat/dynamo_db_functions.js:37` (crp-handle-chat)
- `crp-features -> subproject_id-feature_id-index`
  - `crp-fetch-features/dynamo_db_functions.js:95` (crp-fetch-features)
- `crp-fine-tuning-models -> org-model_name-index`
  - `crp-fetch-fine-tuning-models/dynamo_db_functions.js:84` (crp-fetch-fine-tuning-models)
- `crp-lambda-aws-resources -> org-res_type_res_name-index`
  - `crp-search-aws-resources/dynamo_db_functions.js:37` (crp-search-aws-resources)
  - `crp-search-cloud-resources/dynamo_db_functions.js:41` (crp-search-cloud-resources)
  - `crp-search-cloud-resources/dynamo_db_functions.js:97` (crp-search-cloud-resources)
- `crp-lambda-aws-resources -> res_type-res_name-index`
  - `crp-fetch-cloud-resources/dynamo_db_functions.js:61` (crp-fetch-cloud-resources)
  - `crp-fetch-cloud-resources/dynamo_db_functions.js:87` (crp-fetch-cloud-resources)
  - `crp-search-cloud-resources/dynamo_db_functions.js:70` (crp-search-cloud-resources)
- `crp-openai-platform-store-files -> filename-updated_timestamp-index`
  - `crp-fetch-db-openai-platform-store-files/dynamo_db_functions.js:34` (crp-fetch-db-openai-platform-store-files)
  - `crp-handle-openai-platform-file/dynamo_db_functions.js:54` (crp-handle-openai-platform-file)
  - `crp-openai-platform-store-stream/dynamo_db_functions.js:180` (crp-openai-platform-store-stream)
- `crp-projects -> org-last_checked-index`
  - `crp-check-latest-updated-repos/dynamo_db_functions.js:134` (crp-check-latest-updated-repos)
- `crp-projects -> org-project_name-index`
  - `crp-search-projects/dynamo_db_functions.js:33` (crp-search-projects)
- `crp-sockets -> org-expire-index`
  - `-crp-subprojects-stream-ws/dynamo_db_functions.js:14` (-crp-subprojects-stream-ws)
  - `crp-ai-jobs-stream/dynamo_db_functions.js:19` (crp-ai-jobs-stream)
  - `crp-aws-resources-connections-stream-ws/dynamo_db_functions.js:14` (crp-aws-resources-connections-stream-ws)
  - `crp-aws-resources-stream-ws/dynamo_db_functions.js:14` (crp-aws-resources-stream-ws)
  - `crp-cloud-resources-stream-ws/dynamo_db_functions.js:53` (crp-cloud-resources-stream-ws)
- `crp-subprojects -> org-subproject_name-index`
  - `crp-search-subprojects/dynamo_db_functions.js:36` (crp-search-subprojects)
- `crp-subprojects -> org-updated_timestamp-index`
  - `crp-fetch-subprojects/dynamo_db_functions.js:34` (crp-fetch-subprojects)
- `crp-users -> github_id-index`
  - `crp-check-repo-code-ai/dynamo_db_functions.js:237` (crp-check-repo-code-ai)
