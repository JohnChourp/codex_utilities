# CRP SQS Queues

Purpose: canonical SQS queue reference grounded in the locally downloaded CRP lambda code.

- Region observed in code: `eu-west-1`

## `crp-socket-emitter.fifo`

- Queue URL:
  - `https://sqs.eu-west-1.amazonaws.com/787324535455/crp-socket-emitter.fifo`
- Purpose:
  - Fan out realtime socket updates to the CRP WebSocket management API.

Observed producers:

- `crp-ai-jobs-stream`
- `crp-aws-resources-connections-stream-ws`
- `crp-aws-resources-stream-ws`
- `crp-cloud-resources-stream-ws`
- `crp-create-repo`
- `crp-features-handle-cloud-repos-stream`
- `crp-features-stream-ws`
- `crp-handle-github-webhook`
- `crp-lambda-aws-resources-stream-ws`
- `crp-openai-platform-store-stream`
- `crp-organizations-stream-ws`
- `crp-projects-handle-features-stream`
- `crp-projects-stream-ws`
- `crp-repos-stream-ws`
- `crp-sockets-steam`
- `crp-subprojects-stream-ws`
- `crp-users-stream-ws`
- `crp-ws-cloud-command-response`

Producer evidence:

- `SQS_SOCKET_EMITTER_QUEUE_URL` queue constant and `QueueUrl` usage:
  - `/Users/john/Downloads/lambdas/crp_all/crp-ai-jobs-stream/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-aws-resources-connections-stream-ws/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-aws-resources-stream-ws/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-cloud-resources-stream-ws/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-create-repo/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-features-handle-cloud-repos-stream/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-features-stream-ws/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-handle-github-webhook/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-lambda-aws-resources-stream-ws/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-openai-platform-store-stream/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-organizations-stream-ws/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-projects-handle-features-stream/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-projects-stream-ws/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-repos-stream-ws/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-sockets-steam/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-subprojects-stream-ws/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-users-stream-ws/sqs_functions.js`
  - `/Users/john/Downloads/lambdas/crp_all/crp-ws-cloud-command-response/index.js`

Observed downstream consumer path:

- `crp-socket-emitter-sqs`
  - Uses the WebSocket management endpoint `https://toswnx8m2d.execute-api.eu-west-1.amazonaws.com/production`.
  - Evidence:
    - `/Users/john/Downloads/lambdas/crp_all/crp-socket-emitter-sqs/api_gateway_functions.js`
