# Auth-Drift Search Patterns (CodeDeliver)

Use these patterns when the target is auth-contract drift rather than a single runtime exception.

## Static code smells
- `users\\[0\\]`
- `expiresIn: 2000000`
- `expiresIn: 1209600`
- `jwt.verify`
- `authorizationToken`
- `queryStringParameters.Authorization`
- `queryStringParameters.Authorizer`
- `login_completed`
- `renewing_token`

## Late identity failure signatures
- `no_user_found`
- `user_not_found`
- `user_does_not_exist`
- `delivery_guy_does_not_exist`
- `device_does_not_exist`
- `no_device_found`
- `Unauthorized`

## Useful command style
```bash
rg -n "users\\[0\\]|expiresIn: 2000000|expiresIn: 1209600|jwt.verify|login_completed|no_user_found|user_not_found|user_does_not_exist|delivery_guy_does_not_exist|device_does_not_exist" \
  /home/dm-soft-1/Downloads/lambdas/codeliver_all \
  /home/dm-soft-1/Downloads/projects/codeliver
```

## Per-product targeting
```bash
rg -n "login|renew-token|authorizer|user_does_not_exist|no_user_found" /home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-pos-*
rg -n "login|renew-token|authorizer|user_does_not_exist|no_user_found" /home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-panel-*
rg -n "login|renew-token|authorizer|user_does_not_exist|user_not_found" /home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-sap-*
rg -n "login|renew-device-token|authorizer|delivery_guy_does_not_exist|device_does_not_exist" /home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-app-*
```

## Live log sweep signatures
```bash
aws logs filter-log-events \
  --log-group-name "/aws/lambda/<fn>" \
  --region <region> \
  --start-time <start_ms> \
  --filter-pattern '"user_does_not_exist" || "user_not_found" || "no_user_found" || "delivery_guy_does_not_exist" || "device_does_not_exist" || "Unauthorized" || "502"'
```
