# CodeDeliver socket-emitter payloads (SQS -> WebSocket)

Source of truth

Πηγές (ενδεικτικά, observed από code)
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-panel-socket-emitter-sqs/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-pos-socket-emitter-sqs/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-app-socket-emitter-sqs/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-sap-socket-emitter-sqs/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-panel-devices-stream-ws/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-delivery-requests-stream-ws/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-localserver-ws-connect/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-panel-send-user-cloud-command/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-panel-disconnect-user/index.js`
- `/home/dm-soft-1/Downloads/lambdas/codeliver_all/codeliver-localserver-ws-connect-group-store/index.js`

## Κοινό σχήμα SQS payload (socket-emitter queues)

Κάθε SQS record body είναι JSON array από socket messages.

Observed shape (στα περισσότερα producers)
```json
[
  {
    "connection": "<CONNECTION_ID>",
    "updated_timestamp": 1700000000000,
    "message": {
      "event": "<EVENT_NAME>",
      "data": { "...": "..." }
    }
  }
]
```

Observed special-case shape (panel queue μόνο)
```json
[
  {
    "connection": "<CONNECTION_ID>",
    "updated_timestamp": 1700000000000,
    "panelmessage": {
      "event": "admin-pos-updated",
      "data": { "store_id": "<STORE_ID>", "user_id": "<POS_USER_ID>" }
    }
  }
]
```

Notes
- Τα socket-emitter consumers κάνουν grouping ανά `connection` και forwardάρουν **ολόκληρο** το message object προς WebSocket.
- Το `panelmessage` εμφανίζεται στο `codeliver-pos-users-stream-ws` για panel fanout (observed). Άρα οι panel clients πρέπει να χειρίζονται και τις δύο μορφές (`message` / `panelmessage`).

## Downstream WebSocket envelope (socket-emitter -> clients)

Τα socket-emitter lambdas στέλνουν per-connection ένα envelope με grouped messages.

Observed envelopes
```json
{ "event": "codeliver-panel-grouped-messages", "data": [<SocketMessage>, ...] }
```
```json
{ "event": "codeliver-pos-grouped-messages", "data": [<SocketMessage>, ...] }
```
```json
{ "event": "codeliverapp-grouped-messages", "data": [<SocketMessage>, ...] }
```
```json
{ "event": "codeliver-sap-grouped-messages", "data": [<SocketMessage>, ...] }
```

Localserver clients (observed in `codeliver-localserver-x64`) περιμένουν
```json
{ "event": "localserver-grouped-messages", "data": [<SocketMessage>, ...] }
```

## Event catalog (message.event)

### device-updated
Παράγεται από: `codeliver-panel-devices-stream-ws`.

Required data fields (observed): `group`, `device_id`, `updated_timestamp`.

Example (observed shape)
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "device-updated",
    "data": {
      "group": "<GROUP>",
      "device_id": "<DEVICE_ID>",
      "delivery_guy_id": "<DELIVERY_GUY_ID>",
      "updated_timestamp": 1700000000000
    }
  }
}
```

### device-removed
Παράγεται από: `codeliver-panel-devices-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "device-removed",
    "data": "<DEVICE_ID>"
  }
}
```

### delivery-guy-updated
Παράγεται από: `codeliver-panel-delivery-guys-stream-ws`.

Required data fields (observed): `group`, `delivery_guy_id`, `updated_timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "delivery-guy-updated",
    "data": {
      "group": "<GROUP>",
      "delivery_guy_id": "<DELIVERY_GUY_ID>",
      "mobile": "<MOBILE>",
      "updated_timestamp": 1700000000000
    }
  }
}
```

### delivery-guy-removed
Παράγεται από: `codeliver-panel-delivery-guys-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "delivery-guy-removed",
    "data": "<DELIVERY_GUY_ID>"
  }
}
```

### delivery-guy-coordinates-updated
Παράγεται από: `codeliver-delivery-guy-coordinates-stream-ws`.

Required data fields (observed): `group`, `group_delivery_guy_id`, `timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "delivery-guy-coordinates-updated",
    "data": {
      "group": "<GROUP>",
      "group_delivery_guy_id": "<GROUP>_<DELIVERY_GUY_ID>",
      "timestamp": 1700000000000,
      "lat": 37.98,
      "lng": 23.73
    }
  }
}
```

### request-updated
Παράγεται από: `codeliver-delivery-requests-stream-ws`.

Required data fields (observed): `group`, `store_id`, `request_id`, `updated_timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "request-updated",
    "data": {
      "group": "<GROUP>",
      "store_id": "<STORE_ID>",
      "request_id": "<REQUEST_ID>",
      "updated_timestamp": 1700000000000
    }
  }
}
```

### request-removed
Παράγεται από: `codeliver-delivery-requests-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "request-removed",
    "data": "<REQUEST_ID>"
  }
}
```

### request-actions-updated
Παράγεται από: `codeliver-delivery-request-actions`.

Required data fields (observed): `group_request_id`, `timestamp`, `updated_timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "request-actions-updated",
    "data": {
      "group_request_id": "<GROUP>_<REQUEST_ID>",
      "timestamp": 1700000000000,
      "updated_timestamp": 1700000000000
    }
  }
}
```

### route-updated
Παράγεται από: `codeliver-routes-stream-ws`.

Required data fields (observed): `group`, `route_id`, `updated_timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "route-updated",
    "data": {
      "group": "<GROUP>",
      "route_id": "<ROUTE_ID>",
      "status": "accepted",
      "updated_timestamp": 1700000000000
    }
  }
}
```

### route-removed
Παράγεται από: `codeliver-routes-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "route-removed",
    "data": "<ROUTE_ID>"
  }
}
```

### route-path-updated
Παράγεται από: `codeliver-routes-paths-stream-ws`.

Required data fields (observed): `group`, `route_id`, `path_id`, `updated_timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "route-path-updated",
    "data": {
      "group": "<GROUP>",
      "route_id": "<ROUTE_ID>",
      "path_id": "<PATH_ID>",
      "updated_timestamp": 1700000000000
    }
  }
}
```

### route-path-removed
Παράγεται από: `codeliver-routes-paths-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "route-path-removed",
    "data": "<PATH_ID>"
  }
}
```

### store-updated
Παράγεται από: `codeliver-panel-stores-stream-ws`.

Required data fields (observed): `group`, `store_id`, `updated_timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "store-updated",
    "data": {
      "group": "<GROUP>",
      "store_id": "<STORE_ID>",
      "name": "<STORE_NAME>",
      "updated_timestamp": 1700000000000
    }
  }
}
```

### store-removed
Παράγεται από: `codeliver-panel-stores-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "store-removed",
    "data": "<STORE_ID>"
  }
}
```

### zone-updated
Παράγεται από: `codeliver-panel-group-zones-stream-ws`.

Required data fields (observed): `group`, `zone_id`, `updated_timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "zone-updated",
    "data": {
      "group": "<GROUP>",
      "zone_id": "<ZONE_ID>",
      "name": "<ZONE_NAME>",
      "updated_timestamp": 1700000000000
    }
  }
}
```

### zone-removed
Παράγεται από: `codeliver-panel-group-zones-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "zone-removed",
    "data": "<ZONE_ID>"
  }
}
```

### customer-updated
Παράγεται από: `codeliver-customers-stream-ws`.

Required data fields (observed): `group`, `customer_id`, `updated_timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "customer-updated",
    "data": {
      "group": "<GROUP>",
      "customer_id": "<CUSTOMER_ID>",
      "name": "<CUSTOMER_NAME>",
      "updated_timestamp": 1700000000000
    }
  }
}
```

### customer-removed
Παράγεται από: `codeliver-customers-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "customer-removed",
    "data": "<CUSTOMER_ID>"
  }
}
```

### group-updated
Παράγεται από: `codeliver-groups-stream-ws`.

Required data fields (observed): `group`, `updated_timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "group-updated",
    "data": {
      "group": "<GROUP>",
      "name": "<GROUP_NAME>",
      "updated_timestamp": 1700000000000
    }
  }
}
```

### group-removed
Παράγεται από: `codeliver-groups-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "group-removed",
    "data": "<GROUP>"
  }
}
```

### notification-updated
Παράγεται από: `codeliver-notifications-stream-ws`.

Required data fields (observed): `group`, `notification_id`, `updated_timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "notification-updated",
    "data": {
      "group": "<GROUP>",
      "notification_id": "<NOTIFICATION_ID>",
      "status": "remaining",
      "updated_timestamp": 1700000000000
    }
  }
}
```

### admin-panel-updated
Παράγεται από: `codeliver-panel-users-streams-ws`.

Required data fields (observed): `group`, `user_id`, `updated_timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "admin-panel-updated",
    "data": {
      "group": "<GROUP>",
      "user_id": "<PANEL_USER_ID>",
      "updated_timestamp": 1700000000000
    }
  }
}
```

### admin-panel-removed
Παράγεται από: `codeliver-panel-users-streams-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "admin-panel-removed",
    "data": "<PANEL_USER_ID>"
  }
}
```

### admin-pos-updated
Παράγεται από: `codeliver-pos-users-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "panelmessage": {
    "event": "admin-pos-updated",
    "data": {
      "store_id": "<STORE_ID>",
      "user_id": "<POS_USER_ID>",
      "permissions": ["*"]
    }
  }
}
```

### admin-pos-removed
Παράγεται από: `codeliver-pos-users-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "panelmessage": {
    "event": "admin-pos-removed",
    "data": { "store_id": "<STORE_ID>", "user_id": "<POS_USER_ID>" }
  }
}
```

### admin-sap-updated
Παράγεται από: `codeliver-sap-users-stream-ws`.

Required data fields (observed): `superadmin_id`, `updated_timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "admin-sap-updated",
    "data": { "superadmin_id": "<SAP_USER_ID>", "updated_timestamp": 1700000000000 }
  }
}
```

### admin-sap-removed
Παράγεται από: `codeliver-sap-users-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "admin-sap-removed",
    "data": "<SAP_USER_ID>"
  }
}
```

### localserver-updated
Παράγεται από: `codeliver-localservers-stream-ws`.

Required data fields (observed): `group`, `store_id`, `server_id`, `updated_timestamp`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "localserver-updated",
    "data": {
      "group": "<GROUP>",
      "store_id": "<STORE_ID>",
      "server_id": "<SERVER_ID>",
      "updated_timestamp": 1700000000000
    }
  }
}
```

### localserver-removed
Παράγεται από: `codeliver-localservers-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "localserver-removed",
    "data": { "store_id": "<STORE_ID>", "server_id": "<SERVER_ID>" }
  }
}
```

### localserver
Παράγεται από: `codeliver-localserver-stream-localserverws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "localserver",
    "data": {
      "group": "<GROUP>",
      "store_id": "<STORE_ID>",
      "server_id": "<SERVER_ID>",
      "updated_timestamp": 1700000000000
    }
  }
}
```

### localserver-connection-created
Παράγεται από: `codeliver-localserver-ws-connect`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "localserver-connection-created",
    "data": { "updated_timestamp": 1700000000000 }
  }
}
```

### store (localserver)
Παράγεται από: `codeliver-localserver-ws-connect-group-store`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "store",
    "data": { "group": "<GROUP>", "store_id": "<STORE_ID>", "store_name": "<STORE_NAME>" }
  }
}
```

### charge-updated
Παράγεται από: `codeliver-charges-stream-ws`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": { "event": "charge-updated", "data": { "group": "<GROUP>", "updated_timestamp": 1700000000000 } }
}
```

### user-logout
Παράγεται από: `codeliver-panel-disconnect-user`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": { "event": "user-logout" }
}
```

### cloud-command-response
Παράγεται από: `codeliver-panel-ws-cloud-command-response`, `codeliver-pos-ws-cloud-command-response`, `codeliver-localserver-ws-cloud-command-response`.

Example
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "cloud-command-response",
    "data": { "type": "<COMMAND_TYPE>", "cloud_command_id": 1700000000000, "store_id": "<STORE_ID>" }
  }
}
```

### cloud-command (dynamic)
Παράγεται από: `codeliver-panel-send-user-cloud-command`, `codeliver-panel-send-cloud-command`, `codeliver-panel-device-send-cloud-command`, `codeliver-sap-device-send-cloud-command`.

Observed: `message.event` είναι το `body.type` του HTTP request.

Example (panel -> user)
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "cloud_command_restart_localserver",
    "data": {
      "user_id": "<USER_ID>",
      "cloud_command_id": 1700000000000,
      "group": "<GROUP>",
      "store_id": "<STORE_ID>"
    }
  }
}
```

Example (panel -> localserver)
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "cloud_command_restart_localserver",
    "data": {
      "server_id": "<SERVER_ID>",
      "cloud_command_id": 1700000000000,
      "group": "<GROUP>",
      "store_id": "<STORE_ID>"
    }
  }
}
```

Example (panel/sap -> device)
```json
{
  "connection": "<CONNECTION_ID>",
  "updated_timestamp": 1700000000000,
  "message": {
    "event": "cloud_command_restart_device",
    "data": {
      "device_id": "<DEVICE_ID>",
      "cloud_command_id": 1700000000000,
      "group": "<GROUP>"
    }
  }
}
```

## Σημείωση για επιπλέον producers

Το `codeliver-sockets-kinesis-consumer` παράγει socket-emitter messages από Kinesis records και δημοσιεύει σε panel/pos/app/sap queues. Τα event names και data shapes εξαρτώνται από το payload των records και **δεν** επαναλαμβάνονται εδώ.
