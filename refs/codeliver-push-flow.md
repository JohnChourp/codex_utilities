# codeliver push flow (FCM)

Σκοπός: ροή καταχώρησης push token και αποστολής FCM, με cleanup σε invalid tokens.

Πηγές (observed από code)
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-app-register-push-token/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-send-firebase-push-notification/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-send-firebase-push-notification/README.md`

## Ροή (happy path)

1. Η συσκευή καλεί `codeliver-app-register-push-token` με `firebase_token`.
2. Το token αποθηκεύεται στο `codeliver-devices` και ενημερώνεται `firebase_token_updated_timestamp`.
3. `codeliver-send-firebase-push-notification` στέλνει FCM push με `event.token`, `event.title`, `event.body`.
4. Σε επιτυχία, γίνεται καταγραφή notification στο `codeliver-notifications`.

## Invalid token handling (observed)

- Αν το FCM επιστρέψει `messaging/registration-token-not-registered` ή `messaging/invalid-registration-token`, τότε:
  - Το lambda ρίχνει `CustomError("firebase_token_not_registered")`.
  - Γίνεται clear του `firebase_token` στο `codeliver-devices`.
  - Ο client πρέπει να κάνει re-register (ξανά `codeliver-app-register-push-token`).
