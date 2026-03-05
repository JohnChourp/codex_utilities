# Search Patterns for Cross-Repo Correlation

Use these patterns after extracting identifiers from logs.

## Resource-first
- DynamoDB table names
- SQS queue names / URLs
- SNS topic ARNs
- S3 bucket and key prefixes
- External API host/path

## Flow-first keywords
- `publish`, `emit`, `enqueue`, `sendMessage`, `putItem`, `updateItem`
- `handler`, `process`, `transform`, `map`, `validate`
- `schema`, `version`, `payload`, `contract`

## Id-first
- request id
- correlation id
- store/account/order/user ids

## Typical mismatch signals
- Writer emits field names/types different from reader expectations
- New required field added without backward compatibility
- Partial rollout where one repo uses new schema and another uses old schema
- Silent fallback/default path masking upstream data loss

## Useful command style
```bash
rg -n "<pattern>" <workspace-root>
rg -n "(schema|payload|version|transform)" <repo-path>
git log --oneline -- <file>
```
