# CodeDeliver Projects Guidance (On-Demand)

Use this policy file when the task is project-first/component-first.

## Local paths and assumptions

- Assume project code is already downloaded under:
  - `/home/dm-soft-1/Downloads/projects`
- If user mentions a component/page/screen/module/service/feature, treat it as an end-to-end entrypoint.
- Assume lambdas and projects are connected and may both need scanning.
- Assume `codeliver-app` runs on iOS, Android, and Web (changes must be cross-platform safe).
- For socket-emitter queue behavior changes (grouping/chunking/dedup), also consult/update:
  - `/home/dm-soft-1/Downloads/lambdas/codeliver_all/dm-codeliver-brain/docs/system/README.md`
- If local paths are not accessible in the current execution environment, state it explicitly and provide exact commands for the user to run locally and paste results back.

## Mandatory impact analysis (when project component is mentioned)

Always provide:

1. Impacted lambdas/resources (direct + 1-hop)
2. Potential negative impact / what may break
3. Frontend-change impact on lambdas (when frontend changed)
4. Concise impact summary (integration map only if explicitly requested)

## Minimum scan steps

- Locate component and route usage:
  - `rg -n "MyComponentName|selector:|export class .*Component" /home/dm-soft-1/Downloads/projects`
  - `rg -n "path:.*MyComponentName|loadComponent|loadChildren|component:" /home/dm-soft-1/Downloads/projects`
- Identify service dependencies and API edges:
  - `rg -n "constructor\\(|inject\\(|HttpClient\\b|fetch\\(|axios\\b" /home/dm-soft-1/Downloads/projects`
  - `rg -n "api|endpoint|baseUrl|environment\\.|/v1/|/api/" /home/dm-soft-1/Downloads/projects`
- Map endpoint/event to lambdas via IaC/handlers:
  - `rg -n "httpApi|httpApiEvent|events:|path:|method:|handler:" /home/dm-soft-1/Downloads/lambdas`
  - `rg -n "/your/route/here|detail-type|EventBridge|SNS|SQS|Topic|Queue" /home/dm-soft-1/Downloads/lambdas`
- Expand one hop downstream from identified lambdas:
  - `rg -n "publish\\(|SendMessageCommand|PutEventsCommand|EventBridge|SNS|SQS" /home/dm-soft-1/Downloads/lambdas`
  - `rg -n "DynamoDB|DocumentClient|PutCommand|UpdateCommand|QueryCommand|ScanCommand|S3" /home/dm-soft-1/Downloads/lambdas`
  - `rg -n "<topic-or-queue-or-event-or-table-name>" /home/dm-soft-1/Downloads/lambdas /home/dm-soft-1/Downloads/projects`

## Mandatory validation before closeout

- For every changed lintable source file inside `$HOME/Downloads/projects`, run `npx eslint <changed-file>` from the relevant project root before considering the task done.
- Prefer the project's own `eslint.config.*` or `.eslintrc*`; if the project has no local ESLint config, use the shared fallback at `$HOME/Downloads/projects/eslint.config.mjs`.
- Do not treat a successful `ionic build`, Angular compile, or TypeScript compile as sufficient on its own; ESLint must also pass for the changed files.
- Treat `no-undef`, unresolved imports, and similar static-analysis failures as required fixes, not optional warnings.
- Keep the repo's targeted validation too, such as `npm test`, `npm run lint`, or the narrowest relevant build/test command, when it is available and relevant to the touched files.

## Frontend-to-lambda mapping policy

- Source of truth: `.codex/refs/codeliver-*-lambdas.md`
- If confirmation is still needed, search `*.service.ts` first.
- Expand to other file types only if explicitly requested.
