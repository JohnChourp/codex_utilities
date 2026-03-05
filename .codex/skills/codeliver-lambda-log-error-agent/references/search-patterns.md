# Search Patterns for Cross-Lambda and Frontend Correlation (CodeDeliver)

Use these patterns after extracting identifiers from logs.

## Resource-first
- DynamoDB table names
- SQS queue names / URLs
- SNS topic ARNs
- S3 bucket and key prefixes
- API host/path
- EventBridge detail-type/source

## Flow-first keywords
- `publish`, `emit`, `enqueue`, `SendMessageCommand`, `PutEventsCommand`
- `handler`, `process`, `transform`, `map`, `validate`
- `schema`, `version`, `payload`, `contract`
- `CustomError`, `comment_id`, `presentPostFailureAlert`

## Id-first
- request id
- correlation id
- group/store/user/order ids

## Typical mismatch signals
- Writer emits field names/types different from reader expectations
- New required field added without backward compatibility
- Partial rollout where one lambda uses new schema and another uses old schema
- Frontend caller expects translation key path that backend no longer returns

## Useful command style
```bash
rg -n "<pattern>" /home/dm-soft-1/Downloads/lambdas/codeliver_all /home/dm-soft-1/Downloads/projects/codeliver
rg -n "(schema|payload|version|transform|CustomError|comment_id)" <repo-path>
git log --oneline -- <file>
```
