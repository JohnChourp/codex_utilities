# codeliver WS queues map

Σκοπός: mapping queue → producers/consumers + observed events.

Πηγές (observed από code)
- `sqs_functions.js` των αντίστοιχων producers
- `index.js` των socket-emitter consumers

## Queue: codeliver-panel-socket-emitter.fifo

Queue URL
- `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-panel-socket-emitter.fifo`

Producers (observed references σε `sqs_functions.js`)
- `codeliver-charges-stream-ws`
- `codeliver-customers-stream-ws`
- `codeliver-delivery-guy-coordinates-stream-ws`
- `codeliver-delivery-request-actions`
- `codeliver-delivery-requests-stream-ws`
- `codeliver-groups-stream-ws`
- `codeliver-localserver-ws-cloud-command-response`
- `codeliver-localservers-stream-ws`
- `codeliver-notifications-stream-ws`
- `codeliver-panel-delivery-guys-stream-ws`
- `codeliver-panel-devices-stream-ws`
- `codeliver-panel-disconnect-user`
- `codeliver-panel-group-zones-stream-ws`
- `codeliver-panel-send-user-cloud-command`
- `codeliver-panel-stores-stream-ws`
- `codeliver-panel-users-streams-ws`
- `codeliver-panel-ws-cloud-command-response`
- `codeliver-pos-users-stream-ws`
- `codeliver-routes-paths-stream-ws`
- `codeliver-routes-stream-ws`
- `codeliver-sockets-kinesis-consumer`

Consumer
- `codeliver-panel-socket-emitter-sqs`

Observed events (non-exhaustive)
- `charge-updated`
- `customer-updated`, `customer-removed`
- `delivery-guy-coordinates-updated`
- `request-actions-updated`
- `request-updated`, `request-removed`
- `group-updated`, `group-removed`
- `cloud-command-response`
- `localserver-updated`, `localserver-removed`
- `notification-updated`
- `delivery-guy-updated`, `delivery-guy-removed`
- `device-updated`, `device-removed`
- `user-logout`
- `zone-updated`, `zone-removed`
- `store-updated`, `store-removed`
- `admin-panel-updated`, `admin-panel-removed`
- `admin-pos-updated`, `admin-pos-removed`
- `route-path-updated`, `route-path-removed`
- `route-updated`, `route-removed`
- `cloud_command_*` (dynamic event from `body.type`)

## Queue: codeliver-pos-socket-emitter.fifo

Queue URL
- `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-pos-socket-emitter.fifo`

Producers (observed references σε `sqs_functions.js`)
- `codeliver-customers-stream-ws`
- `codeliver-delivery-requests-stream-ws`
- `codeliver-groups-stream-ws`
- `codeliver-localserver-ws-cloud-command-response`
- `codeliver-panel-delivery-guys-stream-ws`
- `codeliver-panel-send-user-cloud-command`
- `codeliver-panel-stores-stream-ws`
- `codeliver-pos-users-stream-ws`
- `codeliver-pos-ws-cloud-command-response`
- `codeliver-routes-paths-stream-ws`
- `codeliver-routes-stream-ws`
- `codeliver-sockets-kinesis-consumer`

Consumer
- `codeliver-pos-socket-emitter-sqs`

Observed events (non-exhaustive)
- `customer-updated`, `customer-removed`
- `request-updated`, `request-removed`
- `group-updated`, `group-removed`
- `cloud-command-response`
- `delivery-guy-updated`, `delivery-guy-removed`
- `store-updated`, `store-removed`
- `admin-pos-updated`, `admin-pos-removed`
- `route-path-updated`, `route-path-removed`
- `route-updated`, `route-removed`
- `cloud_command_*` (dynamic event from `body.type`)

## Queue: codeliver-app-socket-emitter-sqs.fifo

Queue URL
- `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-app-socket-emitter-sqs.fifo`

Producers (observed references σε `sqs_functions.js`)
- `codeliver-delivery-requests-stream-ws`
- `codeliver-groups-stream-ws`
- `codeliver-notifications-stream-ws`
- `codeliver-panel-delivery-guys-stream-ws`
- `codeliver-panel-device-send-cloud-command`
- `codeliver-panel-devices-stream-ws`
- `codeliver-routes-paths-stream-ws`
- `codeliver-routes-stream-ws`
- `codeliver-sap-device-send-cloud-command`
- `codeliver-sockets-kinesis-consumer`

Consumer
- `codeliver-app-socket-emitter-sqs`

Observed events (non-exhaustive)
- `request-updated`, `request-removed`
- `group-updated`, `group-removed`
- `notification-updated`
- `delivery-guy-updated`, `delivery-guy-removed`
- `device-updated`, `device-removed`
- `route-path-updated`, `route-path-removed`
- `route-updated`, `route-removed`
- `cloud_command_*` (dynamic event from `body.type`)

## Queue: codeliver-sap-socket-emitter.fifo

Queue URL
- `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-sap-socket-emitter.fifo`

Producers (observed references σε `sqs_functions.js`)
- `codeliver-groups-stream-ws`
- `codeliver-panel-stores-stream-ws`
- `codeliver-sap-users-stream-ws`
- `codeliver-sockets-kinesis-consumer`

Consumer
- `codeliver-sap-socket-emitter-sqs`

Observed events (non-exhaustive)
- `group-updated`, `group-removed`
- `store-updated`, `store-removed`
- `admin-sap-updated`, `admin-sap-removed`

## Queue: codeliver-localserver-socket-emitter-sqs.fifo

Queue URL
- `https://sqs.eu-west-1.amazonaws.com/957873067375/codeliver-localserver-socket-emitter-sqs.fifo`

Producers (observed references σε `sqs_functions.js`)
- `codeliver-localserver-stream-localserverws`
- `codeliver-localserver-ws-connect`
- `codeliver-localserver-ws-connect-group-store`
- `codeliver-panel-localserver-remote-login`
- `codeliver-panel-send-cloud-command`
- `codeliver-send-cloud-command`

Consumers
- Δεν υπάρχει consumer lambda στο repo (queue χρησιμοποιείται από localserver websocket emitter).

Observed events (non-exhaustive)
- `localserver`
- `localserver-connection-created`
- `store`
- `remote-login`
- `cloud_command_*` (dynamic event from `body.type`)
