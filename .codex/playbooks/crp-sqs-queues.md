# CRP SQS Queues

Purpose: canonical SQS queue reference grounded in the locally downloaded CRP lambda code.

- Region observed in code: `eu-west-1`

## `crp-socket-emitter.fifo`

- Queue URL:
  - `https://sqs.eu-west-1.amazonaws.com/787324535455/crp-socket-emitter.fifo`
- Purpose:
  - Fan out realtime socket updates to the CRP WebSocket management API.

Observed producers:

- `crp-openai-platform-store-stream`
  - Sends realtime updates after OpenAI platform file processing.
  - Evidence:
    - `/Users/john/Downloads/lambdas/crp_all/crp-openai-platform-store-stream/sqs_functions.js`
    - `/Users/john/Downloads/lambdas/crp_all/crp-openai-platform-store-stream/README.md`
- `crp-subprojects-stream-ws`
  - Sends socket-emitter messages for subproject-related realtime updates.
  - Evidence:
    - `/Users/john/Downloads/lambdas/crp_all/crp-subprojects-stream-ws/sqs_functions.js`

Observed downstream consumer path:

- `crp-socket-emitter-sqs`
  - Uses the WebSocket management endpoint `https://toswnx8m2d.execute-api.eu-west-1.amazonaws.com/production`.
  - Evidence:
    - `/Users/john/Downloads/lambdas/crp_all/crp-socket-emitter-sqs/api_gateway_functions.js`
