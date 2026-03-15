# Authorizer Redaction Audit

Audit date: `2026-03-13`

Scope:
- broad candidate sweep on `dmngr` default branches across `index.js`, `handled_errors.js`, `src/index.js`, `src/handled_errors.js`
- corrected exact rescan on the 264 broad candidates
- classification:
  - `exact`: confirmed regression that breaks authorizer debugging context
  - `review-needed`: repo logs a redacted `event` and uses authorizer context, but the scanned root files do not expose one of the exact bad signatures

Reusable scanner:
- `python3 scripts/scan_authorizer_redaction_regressions.py --org dmngr --json-out /tmp/authorizer-redaction-audit.json --md-out /tmp/authorizer-redaction-audit.md`
- if GitHub GraphQL/network gets flaky, re-run with fewer workers: `--workers 4` or `--workers 1`

Exact bad signatures:
- `SENSITIVE_KEY_RE` (or equivalent) includes `authorizer` or `claims`
- container redaction regex (`PII_CONTAINER_KEY_RE`, `CONTAINER_KEY_RE`, etc.) includes `authorizer` or `claims` and the helper propagates `redactAllLeaves` / `nextRedactAllLeaves`
- explicit redaction mutations such as `delete ...authorizer` or `authorizer: REDACT_VALUE/{}/null/undefined` inside the event-redaction helper

## Summary

- repos scanned in the broad pass: `994`
- candidate repos rescanned for corrected classification: `264`
- confirmed exact hits: `2`
- review-needed repos: `161`

Top review-needed families:
- `codeliver`: 61
- `paneldelivery`: 33
- `dm`: 23
- `superadminpanel`: 9
- `bridges`: 6
- `superadminPanel`: 5

## Confirmed Exact Hits

### `paneldelivery-get-store-basic-data`

Signature:
- `SENSITIVE_KEY_RE` includes `authorizer`, so `requestContext.authorizer` collapses to `[REDACTED]` in the redacted error-event log

Observed lines on default branch:
- `const SENSITIVE_KEY_RE = /(authorization|authorizationtoken|authorizer|cookie|set-cookie|x-api-key|x-amz-security-token|token|password|secret)/i;`
- `out[k] = SENSITIVE_KEY_RE.test(k) ? REDACT_VALUE : redactDeep(v, seen);`
- `console.log("event", jsonStringifySafe(redactDeep(event)));`

### `paneldelivery-handle-customer-address`

Signature:
- `PII_CONTAINER_KEY_RE` includes `authorizer|claims`
- helper propagates `redactAllLeaves`, so the entire `requestContext.authorizer` / claims subtree gets flattened to `[REDACTED]`

Observed lines on default branch:
- `const PII_CONTAINER_KEY_RE =`
- `/^(address|authorizer|claims|customer_id|doorbellname|email|first_name|identity|ip|last_name|mobile|name|phone|principalid|sourceip|sub|useragent|x-forwarded-for)$/i;`
- `function redactDeep(value, seen = new WeakSet(), redactAllLeaves = false) {`
- `const nextRedactAllLeaves = redactAllLeaves || PII_CONTAINER_KEY_RE.test(k);`

## Review-Needed Inventory

These repos should be swept next because they log a redacted `event` and also depend on `requestContext.authorizer` / `authorizer.jwt.claims`, even though the scanned root files did not expose one of the exact signatures above.

- `add_store_customer`
- `alpha-create-client-token`
- `athena-store-stats`
- `bridges-bris-create-order-file`
- `bridges-elink-create-order-file`
- `bridges-fetch-bridge-data-versions`
- `bridges-get-data`
- `bridges-megasoft-create-order-file`
- `bridges-save-data`
- `checkStoreAndClientNotificationPreferences`
- `codeliver-apifon`
- `codeliver-apifon-webhook`
- `codeliver-app-async-actions`
- `codeliver-app-authorizer`
- `codeliver-app-delivery-guys-actions-handler`
- `codeliver-app-fetch-delivery-guy-data`
- `codeliver-app-fetch-delivery-requests`
- `codeliver-app-fetch-notifications`
- `codeliver-app-get-requests-stats`
- `codeliver-app-renew-device-token`
- `codeliver-app-sync-actions`
- `codeliver-app-ws-connect`
- `codeliver-backend-check-delivery-requests`
- `codeliver-external-request-cancel`
- `codeliver-fetch-delivery-guy-raw-coordinates`
- `codeliver-panel-connectivity-stats`
- `codeliver-panel-delivery-request-calculations`
- `codeliver-panel-device-send-cloud-command`
- `codeliver-panel-disconnect-user`
- `codeliver-panel-fetch-charges`
- `codeliver-panel-fetch-delivery-guy-path`
- `codeliver-panel-fetch-delivery-guys`
- `codeliver-panel-fetch-delivery-guys-actions`
- `codeliver-panel-fetch-delivery-guys-positions`
- `codeliver-panel-fetch-delivery-requests-actions`
- `codeliver-panel-fetch-devices`
- `codeliver-panel-fetch-localserver-logs`
- `codeliver-panel-fetch-localserver-sockets`
- `codeliver-panel-fetch-localservers`
- `codeliver-panel-fetch-orphan-localservers`
- `codeliver-panel-fetch-panel-users`
- `codeliver-panel-fetch-pos-users`
- `codeliver-panel-fetch-users-sockets`
- `codeliver-panel-get-requests-stats`
- `codeliver-panel-get-store-stats-devices`
- `codeliver-panel-handle-delivery-customer`
- `codeliver-panel-handle-delivery-guy`
- `codeliver-panel-handle-delivery-guy-shift`
- `codeliver-panel-handle-device`
- `codeliver-panel-handle-localserver`
- `codeliver-panel-handle-panel-user`
- `codeliver-panel-handle-pos-user`
- `codeliver-panel-localserver-remote-login`
- `codeliver-panel-reorder-delivery-guys`
- `codeliver-panel-reorder-stores`
- `codeliver-panel-reorder-zones`
- `codeliver-panel-search-group-charges`
- `codeliver-panel-search-group-delivery-customers`
- `codeliver-panel-search-localserver-logs`
- `codeliver-panel-search-notifications`
- `codeliver-panel-send-cloud-command`
- `codeliver-panel-send-user-cloud-command`
- `codeliver-pos-handle-customer`
- `codeliver-pos-handle-store`
- `codeliver-pos-renew-token`
- `codeliver-pos-search-delivery-requests`
- `codeliver-sap-fetch-admin-sockets`
- `codeliver-sap-fetch-groups`
- `codeliver-sap-handle-group`
- `codeliver-sap-send-user-credentials`
- `codeliver-send-cloud-command`
- `customers_newsletter_coupon_rule`
- `customers_socket_stream`
- `dm-codeliver-precalculate-request`
- `dm-format-receipt-data`
- `dm-init-store-customers-attrs`
- `dm-kiosk-app-abort-cashdro-session`
- `dm-kiosk-app-check-one-time-password`
- `dm-kiosk-app-check-pos-terminal-session-status`
- `dm-kiosk-app-customer-register`
- `dm-kiosk-app-initiate-cardlink-transaction`
- `dm-kiosk-app-initiate-pos-terminal-transaction`
- `dm-kiosk-app-void-cardlink-transaction`
- `dm-loyaltyapp-kiosk-add-customer-product`
- `dm-loyaltyapp-kiosk-create-coupon`
- `dm-loyaltyapp-kiosk-fetch-customer-data`
- `dm-loyaltyapp-kiosk-fetch-ranking`
- `dm-loyaltyapp-kiosk-remind-member-number`
- `dm-loyaltyapp-kiosk-renew-token`
- `dm-loyaltyapp-kiosk-submit-customer-form`
- `dm-rdc-update-customers`
- `dm-send-deleted-customer-questionnaire`
- `dm-send-navigation-to-bank-modal-socket`
- `dm-update-vat-customers-addresses-sqs-trigger`
- `dm-vat-customers-addresses-to-customers-sqs-trigger`
- `dm-wolt-orders-webhook`
- `eurobank-create-client-token`
- `export-group-mobiles`
- `export-store-emails`
- `get_user_data`
- `hotel_delivery_calculate_final_price`
- `hotel_delivery_create_order`
- `migration-points-csv-to-db`
- `mo_users_renew_token`
- `mobileorder-fetch-loyaltyapp-ranking`
- `mobileorder-handle-reservation`
- `mypos-checkout-recurring`
- `mypos-create-client-token`
- `paneldelivery-cardlink-test-transaction`
- `paneldelivery-coupon-sms-message`
- `paneldelivery-delivery-services-get-estimations`
- `paneldelivery-epay-communication-test`
- `paneldelivery-epay-initiate-transaction`
- `paneldelivery-export-contest-draws`
- `paneldelivery-fetch-category-products`
- `paneldelivery-fetch-contest-draws`
- `paneldelivery-fetch-customer-addresses`
- `paneldelivery-fetch-customer-points`
- `paneldelivery-fetch-customer-review-preferences`
- `paneldelivery-fetch-customer-vats`
- `paneldelivery-fetch-group-customers`
- `paneldelivery-fetch-loyaltyapp-customer-products`
- `paneldelivery-fetch-points`
- `paneldelivery-fetch-points-customers-ranking`
- `paneldelivery-fetch-product-connections-details`
- `paneldelivery-fetch-product-customer-prices`
- `paneldelivery-fetch-store-audiences-stats`
- `paneldelivery-fetch-store-charges-refunds`
- `paneldelivery-get-customer`
- `paneldelivery-handle-order-delivery-service`
- `paneldelivery-handle-store-reservation`
- `paneldelivery-kiosk-app-handle-user`
- `paneldelivery-pos-terminal-test-transaction`
- `paneldelivery-precheck-full-connection`
- `paneldelivery-save-contest-winners`
- `paneldelivery-search-customer-addresses`
- `paneldelivery-search-customer-draws`
- `paneldelivery-search-customer-points-ranking`
- `paneldelivery-search-group-customers`
- `paneldelivery-search-points`
- `paneldelivery-update-customer-data`
- `paneldelivery_answer_review`
- `paneldelivery_create_coupon`
- `paneldelivery_handle_user`
- `paneldelivery_reviews_customer_id_init`
- `paneldelivery_store_charges`
- `superadminPanel-fetch-charges`
- `superadminPanel-fetch-customer-review-preferences`
- `superadminPanel-fetch-customers`
- `superadminPanel-find-old-group-audiences`
- `superadminPanel-search-charges`
- `superadminpanel-answer-review`
- `superadminpanel-create-new-store`
- `superadminpanel-fetch-invoicing-credentials`
- `superadminpanel-fetch-store-charges`
- `superadminpanel-fetch-store-credits`
- `superadminpanel-handle-invoicing-credentials`
- `superadminpanel-handle-store-charge`
- `superadminpanel-handle-store-credit`
- `superadminpanel-search-customers`
- `unsubscribe-save-data`

## How To Use This In A Sweep

- fix the `2` exact hits first; these are clear harden regressions
- when running `crp repos harden-pr` across the review-needed list, explicitly inspect the event-redaction helper before trusting `ctx` logs
- keep exact hits and review-needed repos separate in change summaries / PR descriptions
