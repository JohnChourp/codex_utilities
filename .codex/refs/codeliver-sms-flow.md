# codeliver SMS flow (apifon)

Σκοπός: συνοπτική ροή SMS από request μέχρι update στο `codeliver-notifications`.

Πηγές (observed από code)
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-send-sms-gateway/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-sms-sqs-dispatcher/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-apifon/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-apifon-webhook/index.js`

## Ροή (happy path)

1. `codeliver-send-sms-gateway` αποφασίζει gateway (default/apifon) και κάνει direct invoke ή enqueue.
2. `codeliver-sms-sqs-dispatcher` καταναλώνει SQS batch και κάνει invoke `codeliver-apifon` όταν `gateway === "apifon"`.
3. `codeliver-apifon` στέλνει SMS μέσω Apifon και γράφει εγγραφή στο `codeliver-notifications`.
4. Apifon callback → `codeliver-apifon-webhook` ενημερώνει το `codeliver-notifications` (`successful`/`failed`).
5. `codeliver-notifications-stream-ws` διαδίδει update προς panel/app sockets.

## Σημεία αποτυχίας (observed)

- `codeliver-send-sms-gateway`:
  - Αν λείπει `gateway` ή misconfig, επιστρέφει `no_gateway_set`.
  - Αν αποτύχει `lambda_invoke` προς `codeliver-apifon`, επιστρέφει `lambda_invoke_apifon_error`.
- `codeliver-sms-sqs-dispatcher`:
  - Αν το `codeliver-apifon` επιστρέψει `success:false`, το SQS batch αποτυγχάνει και γίνεται retry.
- `codeliver-apifon`:
  - Missing `APIFON_SECRET`/`APIFON_TOKEN` ή invalid signature → `status: failed` στο notification.
  - DB failure → `success:false`.
- `codeliver-apifon-webhook`:
  - Αν δεν βρει `notification_id`, logάρει και επιστρέφει `success:true` χωρίς update.
