# CodeDeliver external integrations (canonical)

Source of truth

Πηγές (observed από code)
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-apifon/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-apifon/README.md`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-send-firebase-push-notification/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-send-firebase-push-notification/README.md`

## Apifon (SMS)

Canonical endpoint
- `https://ars.apifon.com/services/api/v1/sms/send`

Canonical callback URL (hard-coded στο lambda `codeliver-apifon`)
- `https://8n41kfc8o5.execute-api.eu-west-1.amazonaws.com/codeliver-apifon-webhook`

Required env vars
- `APIFON_SECRET`
- `APIFON_TOKEN`

Observed usage
- `codeliver-apifon` κάνει HMAC signature και καλεί Apifon με `sender_id = event.headings`.
- `codeliver-apifon-webhook` ενημερώνει το `codeliver-notifications` με βάση `notification_id`.

## Firebase / FCM (push)

Service account
- `codeliver-send-firebase-push-notification` κάνει `process.env.GOOGLE_APPLICATION_CREDENTIALS = "./codeliver-app.json"`.

Canonical error codes (observed)
- `messaging/registration-token-not-registered`
- `messaging/invalid-registration-token`

Observed error handling
- Για τα παραπάνω FCM error codes, το lambda ρίχνει `CustomError("firebase_token_not_registered")` και κάνει clear το `firebase_token` στο `codeliver-devices`.

Observed inputs (minimum)
- `event.group`, `event.delivery_guy_id`, `event.device_id`, `event.token`, `event.title`, `event.body`.
