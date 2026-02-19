# codeliver-notifications usage map

Σκοπός: ποιοι γράφουν/διαβάζουν/streamάρουν το `codeliver-notifications`.

Πηγές (observed από code)
- `rg -l "TableName: \"codeliver-notifications\"" /home/dm-soft-1/Downloads/lambdas/codeliver_all -g "*.js"`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-notifications-stream-ws/index.js`

## Writers (Put/Update)

- `codeliver-apifon` (PutItem)
- `codeliver-apifon-webhook` (UpdateItem by `notification_id`)
- `codeliver-send-firebase-push-notification` (PutItem)
- `codeliver-app-delivery-guys-actions-handler` (UpdateItem για `read_notification`)

## Readers (Query)

- `codeliver-sms-sqs-dispatcher` (de-duplication για SMS)
- `codeliver-send-sms-gateway` (rate-limit / recent SMS check)
- `codeliver-app-fetch-notifications` (app UI)
- `codeliver-panel-search-notifications` (panel UI)

## Stream consumers (DynamoDB Streams)

- `codeliver-notifications-stream-ws` (fanout προς panel/app socket-emitter queues)

## Notes

- Όλες οι παραπάνω ροές βασίζονται σε `notification_id` και `updated_timestamp` για ordering/updates.
- Αν αλλάξει το schema στο `codeliver-notifications`, επηρεάζονται τα query filters και τα websocket updates.
