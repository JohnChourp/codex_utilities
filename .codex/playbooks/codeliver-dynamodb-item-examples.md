# CodeDeliver DynamoDB Item Examples (canonical)

<INSTRUCTIONS>
Purpose
- This playbook complements:
  - `.codex/playbooks/codeliver-dynamodb-keys-and-indexes.md`
- The keys playbook is the single source of truth for:
  - PK/SK names, GSI/LSI names, index key attributes and types
- This playbook is the single source of truth for:
  - What real DynamoDB items look like per table (non-key attributes, common shapes, “entity” variants)
  - Sanitized, representative example items that match production/dev reality

Non-negotiable rules

- DO NOT invent attributes, entity types, or value formats.
- Only add/modify attributes after verifying from one (or more) of:
  1. IaC templates / table definitions
  2. Lambda/project code that writes/updates/reads items
  3. Real DynamoDB items from a non-prod environment (sanitized)
- If index key names/types are missing or unclear:
  - Update `.codex/playbooks/codeliver-dynamodb-keys-and-indexes.md` first (canonical), then reference it here.
- Keep examples sanitized:
  - Replace PII (names, phones, emails, addresses), tokens, secrets, device identifiers, and internal IDs with placeholders.
  - Keep formats consistent (UUID vs numeric ID vs prefixed IDs), but never leak real values.

Preferred example format

- Use DocumentClient-style JSON (plain JS object) for examples, because lambdas are Node.js and typically use `@aws-sdk/lib-dynamodb`.
- Optionally include a second “DynamoDB JSON” example (with `{"S":...,"N":...}`) when useful for AWS CLI parity.

Minimum content per table (required)
For every DynamoDB table listed in `.codex/playbooks/codeliver-dynamodb-keys-and-indexes.md`, add a section containing:

1. Table name/alias (exactly as referenced in keys playbook)
2. Link/reference back to keys playbook section for this table
3. “Entity types / item categories” found in real data (if single-table design, this is mandatory)
4. Non-key attributes:
   - Required attributes (must exist)
   - Optional attributes (often present)
   - TTL / timestamps / versioning fields (if present)
5. At least:
   - 1 “happy-path” example item per entity type
   - 1 “edge/failure-prone” example item per table (e.g. missing optional fields, soft-deleted, TTL soon, etc.)
6. Notes:
   - Any attribute-level invariants (e.g. enum-like values, state transitions)
   - Idempotency/versioning strategy (if present)
   - Any known “sparse” attributes (exist only for some entities)

How to update this playbook (local workflow)
A) From code (recommended baseline)

- Identify all writes:
  - `PutCommand`, `UpdateCommand`, `BatchWriteCommand`, `TransactWriteCommand`
- Identify all reads and projections:
  - `GetCommand`, `QueryCommand`, `ScanCommand`, `TransactGetCommand`
- Capture:
  - Full `Item` shapes
  - `ExpressionAttributeNames/Values` used in updates
  - Any mapping functions (e.g. `toItem()`, `fromItem()`, `marshall/unmarshall`, DTOs)

B) From real DynamoDB items (recommended to validate reality)

- In a non-prod AWS account/environment:
  - Scan a small number of items per table
  - Sanitize
  - Group by entity type (often derivable from SK prefix, a `type/entityType` attribute, or discriminator fields)
- Paste representative examples here.

Sanitization guidelines (mandatory)

- Replace values, preserve structure:
  - IDs: `"<ID>"`, `"COURIER#<ID>"`, `"DELIVERY#<ID>"`
  - Emails: `"<EMAIL>"`
  - Phone numbers: `"<PHONE>"`
  - Device tokens: `"<DEVICE_TOKEN>"`
  - Addresses/geo: `"<ADDRESS>"`, `{"lat": <LAT>, "lng": <LNG>}` (rounded / placeholder)
  - JWT/API keys: `"<REDACTED>"`
- Do not include:
  - Real names, real addresses, real tokens/keys, real device identifiers

</INSTRUCTIONS>

---

## Tables

NOTE

- All example values below are sanitized placeholders (structure preserved, sensitive values removed).
- Where an example is missing, the section is marked `TBD` (no guessing).

---

## Table: codeliver-batches

Source of truth

- Keys & indexes: `.codex/playbooks/codeliver-dynamodb-keys-and-indexes.md` (codeliver-batches)

Entity types / item categories

- batch (per `group_delivery_guy_id` + `batch_id`)

Example items (DocumentClient JSON)

### batch — last 10 items (timestamp-sorted scan) union example (sanitized)

```json
{
  "group_delivery_guy_id": "<GROUP>_<DELIVERY_GUY_ID>",
  "batch_id": 123,
  "closed_by_delivery_guy_timestamp": "<EPOCH_MS_STRING>",
  "shift_work_time": "<SHIFT_DURATION>",
  "timestamp": "<EPOCH_MS_STRING>",
  "total_delivery_cost": 21.6,
  "total_delivery_guy_compensation": 17.3,
  "total_delivery_guy_income": 4.3,
  "total_requests_amount_card": 0,
  "total_requests_amount_card_and_cash": 7.45,
  "total_requests_amount_cash": 7.45,
  "total_requests_count": 11,
  "total_tips": 3
}
```

Table: codeliver-customers

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-customers)

Entity types / item categories

customer profile (per store_id + customer_id)

Example items (DocumentClient JSON)

customer — observed example (sanitized)

```
{
  "store_id": "<STORE_ID>",
  "customer_id": "<CUSTOMER_ID>",
  "addresses": [
    {
      "addressComments": null,
      "address_components": {
        "city": "<CITY>",
        "postal_code": "<POSTAL_CODE>",
        "state": null,
        "street": "<STREET>",
        "street_number": "<STREET_NUMBER>",
        "user_point_postal_code": null
      },
      "address_id": "<ADDRESS_ID>",
      "distanceInStraightLine": 4138,
      "distanceKm": "4.14 km",
      "distanceValue": 4138,
      "distance_by_store_id": {
        "<STORE_ID>": 4138
      },
      "doorbellname": null,
      "floor": null,
      "formatted_address": "<FORMATTED_ADDRESS>",
      "googleLat": 0,
      "googleLng": 0,
      "isClicked": true,
      "radius_distance_by_store_id": {
        "<STORE_ID>": 4.14
      },
      "unverified": false,
      "updated_by_admin": true,
      "userLat": 0,
      "userLng": 0,
      "zone_id": "<ZONE_ID>"
    }
  ],
  "created_by_user_id": "<CREATED_BY_USER_ID>",
  "firstName": "<FIRST_NAME>",
  "group": "<GROUP>",
  "lastName": "<LAST_NAME>",
  "phone": "<PHONE>",
  "storeEmail": null,
  "storeName": "<STORE_NAME>",
  "storePhone": "<STORE_PHONE>",
  "store_address": {
    "addressComments": null,
    "address_components": {
      "city": "<CITY>",
      "postal_code": "<POSTAL_CODE>",
      "state": null,
      "street": "<STREET>",
      "street_number": "<STREET_NUMBER>",
      "user_point_postal_code": null
    },
    "address_id": "<STORE_ADDRESS_ID>",
    "doorbellname": null,
    "floor": null,
    "formatted_address": "<STORE_FORMATTED_ADDRESS>",
    "googleLat": 0,
    "googleLng": 0,
    "unverified": false,
    "updated_by_admin": true,
    "userLat": 0,
    "userLng": 0
  },
  "timestamp": "<EPOCH_MS_STRING>"
}
```

Table: codeliver-delivery-guys

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-delivery-guys)

Entity types / item categories

delivery guy profile (per group + delivery_guy_id)

Example items (DocumentClient JSON)

delivery guy — observed example (sanitized)

```
{
  "group": "<GROUP>",
  "delivery_guy_id": "<DELIVERY_GUY_ID>",
  "admin": true,
  "arrived_to_customer_estimated_delay": 0,
  "batchNumber": 2,
  "current_device_id": "<DEVICE_ID>",
  "delivery_guy_income": 1,
  "delivery_guy_type": "delivery_guy_device",
  "device_id": "<DEVICE_ID>",
  "group_delivery_guy_id": "<GROUP>_<DELIVERY_GUY_ID>",
  "language_code": "el",
  "last_closed_batch_by_delivery_guy_timestamp": "<EPOCH_MS_STRING>",
  "max_requests_in_route": 1,
  "mobile": "<PHONE>",
  "name": "<NAME>",
  "password": "<BCRYPT_HASH>",
  "permissions": [
    "*"
  ],
  "settings": {
    "font_settings": {
      "scale": 0.5000000000000001
    },
    "local_notifications_settings": {
      "enabled": true
    },
    "push_notifications_settings": {
      "enabled": true
    },
    "sounds_settings": {
      "enabled": true,
      "loop_number": 3,
      "selected_sound": "whistling"
    },
    "vibration_settings": {
      "enabled": true
    }
  },
  "simulation": false,
  "status": "available",
  "updated_timestamp": 1767166997531,
  "zoneId": "<ZONE_ID>"
}
```

Table: codeliver-delivery-guys-actions

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-delivery-guys-actions)

Entity types / item categories

delivery guy action / audit event

Example items (DocumentClient JSON)

action — observed example (sanitized)

```
{
  "group_delivery_guy_id": "<GROUP>_<DELIVERY_GUY_ID>",
  "timestamp": "<EPOCH_MS_STRING>",
  "data": {
    "path_id": "<PATH_ID>",
    "path_type": "store_to_customer",
    "request_id": "<REQUEST_ID>",
    "route_id": "<ROUTE_ID>",
    "status": "completed"
  },
  "delivery_guy_id": "<DELIVERY_GUY_ID>",
  "device_id": "<DEVICE_ID>",
  "expire": 1769007503,
  "group": "<GROUP>",
  "path_id": "<PATH_ID>",
  "request_id": "<REQUEST_ID>",
  "route_id": "<ROUTE_ID>",
  "type": "route_path_status"
}
```

Table: codeliver-delivery-guys-coordinates

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-delivery-guys-coordinates)

Entity types / item categories

coordinate ping / tracking record

Example items (DocumentClient JSON)

coordinate — observed example (sanitized)

```
{
  "group_delivery_guy_id": "<GROUP>_<DELIVERY_GUY_ID>",
  "timestamp": "<EPOCH_MS_STRING>",
  "accuracy": 1,
  "delivery_guy_id": "<DELIVERY_GUY_ID>",
  "device_id": "<DEVICE_ID>",
  "expire": 1769330475,
  "group": "<GROUP>",
  "lat": 0,
  "lng": 0,
  "paused": false,
  "registeredTimestamp": "<EPOCH_MS_STRING>",
  "speed": 0.00009639030925031462
}
```

Table: codeliver-delivery-guys-connections

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-delivery-guys-connections)

Entity types / item categories

group delivery-guy connectivity analytics per UTC 30-minute slot (peak by slot)

Example items (DocumentClient JSON)

slot peak — observed shape (sanitized)

```
{
  "group": "<GROUP>",
  "day": "2026-02-12#10:30",
  "year_month": "2026-02",
  "peak_count": 7,
  "peak_time_utc": "10:37:19",
  "updated_timestamp": 1767177439000
}
```

same slot updated with higher peak (conditional upsert keeps max)

```
{
  "group": "<GROUP>",
  "day": "2026-02-12#10:30",
  "year_month": "2026-02",
  "peak_count": 9,
  "peak_time_utc": "10:44:03",
  "updated_timestamp": 1767177843000
}
```

different slot in same day (distinct SK)

```
{
  "group": "<GROUP>",
  "day": "2026-02-12#11:00",
  "year_month": "2026-02",
  "peak_count": 6,
  "peak_time_utc": "11:05:10",
  "updated_timestamp": 1767179110000
}
```

Table: codeliver-devices

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-devices)

Entity types / item categories

device profile

Example items (DocumentClient JSON)

device — observed example (sanitized)

```
{
  "group": "<GROUP>",
  "device_id": "<DEVICE_ID>",
  "active": true,
  "admin": true,
  "delivery_guy_id": "<DELIVERY_GUY_ID>",
  "device_type": "delivery_guy_device",
  "firebase_token": "<FCM_REGISTRATION_TOKEN>",
  "firebase_token_updated_timestamp": "<EPOCH_MS_STRING>",
  "language_code": "el",
  "name": "<NAME>",
  "password": "<BCRYPT_HASH>",
  "updated_timestamp": "<EPOCH_MS_STRING>"
}
```

Table: codeliver-devices-sockets

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-devices-sockets)

Entity types / item categories

websocket session record (device)

Example items (DocumentClient JSON)

socket — observed example (sanitized)

```
{
  "connection": "<CONNECTION_ID>",
  "expire": 1767174434,
  "delivery_guy_id": "<DELIVERY_GUY_ID>",
  "device_id": "<DEVICE_ID>",
  "group": "<GROUP>",
  "group_delivery_guy_id": "<GROUP>_<DELIVERY_GUY_ID>",
  "group_device_id": "<GROUP>_<DEVICE_ID>",
  "sourceIp": "<IP_ADDRESS>",
  "updated_timestamp": 1767167234402
}
```

Table: codeliver-group-zones

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-group-zones)

Entity types / item categories

zone configuration (per group + zone_id)

Example items (DocumentClient JSON)

zone — observed example (sanitized + trimmed lists/maps)

```
{
  "group": "<GROUP>",
  "zone_id": "<ZONE_ID>",
  "active": true,
  "area": "<AREA>",
  "deliveryGuysCount": 24,
  "deliveryGuysNames": [
    "<NAME_1>",
    "<NAME_2>",
    "<NAME_3>"
  ],
  "delivery_areas": [
    {
      "active": true,
      "boundaries": "<BOUNDARIES_CSV>",
      "calculation_type": "path",
      "comment": null,
      "deliveryCost": 0,
      "delivery_cost_per_kilometer_active": false,
      "fillColor": "#FFCC00",
      "fillOpacity": 0.3,
      "free_delivery_over_amount": 0,
      "label": "<LABEL_1>",
      "minOrder": 0,
      "source": "origin",
      "store_delivery_costs": {
        "default_cost": 1.8,
        "delivery_guy_compensation": 1.5,
        "store_costs": {
          "<STORE_ID_1>": 2,
          "<STORE_ID_2>": 1.7,
          "<STORE_ID_3>": 1.8
        }
      },
      "strokeColor": "#0000FF",
      "timestamp": "<EPOCH_MS_STRING>",
      "type": "polygon"
    },
    {
      "active": true,
      "boundaries": "<BOUNDARIES_CSV>",
      "calculation_type": "path",
      "comment": null,
      "deliveryCost": 0,
      "delivery_cost_per_kilometer_active": false,
      "fillColor": "#FFCC00",
      "fillOpacity": 0.3,
      "free_delivery_over_amount": 0,
      "label": "<LABEL_2>",
      "minOrder": 0,
      "source": "origin",
      "store_delivery_costs": {
        "default_cost": 2.6,
        "delivery_guy_compensation": 2.3,
        "store_costs": {
          "<STORE_ID_1>": 2.8,
          "<STORE_ID_2>": 2.5,
          "<STORE_ID_3>": 2.6
        }
      },
      "strokeColor": "#0000FF",
      "timestamp": "<EPOCH_MS_STRING>",
      "type": "polygon"
    },
    {
      "active": true,
      "boundaries": "<BOUNDARIES_CSV>",
      "calculation_type": "path",
      "comment": null,
      "deliveryCost": 0,
      "delivery_cost_per_kilometer_active": false,
      "fillColor": "#FFCC00",
      "fillOpacity": 0.3,
      "free_delivery_over_amount": 0,
      "label": "<LABEL_3>",
      "minOrder": 0,
      "source": "origin",
      "store_delivery_costs": {
        "default_cost": 3.5,
        "delivery_guy_compensation": 3,
        "store_costs": {
          "<STORE_ID_1>": 3.5,
          "<STORE_ID_2>": 3,
          "<STORE_ID_3>": 3.2
        }
      },
      "strokeColor": "#0000FF",
      "timestamp": "<EPOCH_MS_STRING>",
      "type": "polygon"
    }
  ],
  "delivery_guy_income": 1,
  "disable_requests_creation_to_stores_inside_zone": false,
  "updated_timestamp": 1767021500340,
  "_updated_timestamp": 1767021500340
}
```

Table: codeliver-groups

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-groups)

Entity types / item categories

group configuration (single item per group)

Example items (DocumentClient JSON)

group config — observed example (sanitized)

```
{
  "group": "<GROUP>",
  "allowed_delivery_guys_types": [
    "delivery_guy_device"
  ],
  "allow_panel_pages": [
    "requests",
    "customers",
    "routes",
    "delivery-guys",
    "devices",
    "zones",
    "stores",
    "notifications",
    "statistics",
    "charges",
    "admins-panel",
    "admins-pos",
    "settings"
  ],
  "allow_pos_pages": [
    "requests",
    "customers",
    "statistics"
  ],
  "allow_requests_over_ready_horizon": true,
  "allow_requests_preparation_time": false,
  "allow_requests_ready_to_pickup_action": false,
  "allow_routes_creation_by_store_accounts": false,
  "allow_store_pages": [
    "requests"
  ],
  "arrived_to_customer_estimated_delay": 1,
  "balance": -1.575,
  "canceled_requests_reasons": [],
  "default_missing_eta_travel_time_sec": 600,
  "delivery_guy_requests_rejected_reasons": [],
  "distance_only_mode": false,
  "drop_service_time_sec": 60,
  "enable_request_custom_order_id": true,
  "expiration_time": 60,
  "fast_simulation": false,
  "filename": "<FILE_ID>.png",
  "filename_flat": "<FILE_ID>.png",
  "haversine_distance_factor": 1.2,
  "hide_requests_step_info": false,
  "hide_simulation": false,
  "languages": [
    {
      "code": "en",
      "mm_base": false,
      "mo_base": false,
      "status": true,
      "title": "ENGLISH"
    },
    {
      "code": "el",
      "mm_base": true,
      "mo_base": true,
      "status": true,
      "title": "ΕΛΛΗΝΙΚΑ"
    }
  ],
  "last_short_cf_request_id": 116,
  "max_allowed_zones": 1,
  "max_break_minutes": 20,
  "max_requests_in_route": 5,
  "max_route_duration_sec": 3600,
  "max_total_distance_m": 10000,
  "name": "<GROUP_DISPLAY_NAME>",
  "panel_domain_url": "<PANEL_DOMAIN>",
  "panel_under_maintenance": false,
  "pickup_service_time_sec": 60,
  "plan": "simple",
  "pos_domain_url": "<POS_DOMAIN>",
  "pos_under_maintenance": false,
  "ready_horizon_sec": 900,
  "requests_custom_options": {
    "address_location": {
      "active": true,
      "choices": [
        {
          "choice_id": "in_city",
          "selected": true,
          "translations": [
            {
              "el": "Εντός Πόλης",
              "en": "In City"
            }
          ]
        },
        {
          "choice_id": "out_city",
          "selected": false,
          "translations": [
            {
              "el": "Εκτός Πόλης",
              "en": "Out City"
            }
          ]
        }
      ],
      "type": "radio"
    }
  },
  "requests_enable_customers_selection": false,
  "requests_required_address": false,
  "request_default_preparation_time": 3,
  "sender_id": "<SENDER_ID>",
  "short_order_id_prefix": "A",
  "simulation": false,
  "test_routes_merge": false,
  "timestamp": 1763128847678,
  "uniqueRequestOrderNumber": 974,
  "updated_timestamp": 1767095347495,
  "urban_speed_mps": 10
}
```

Table: codeliver-localserver-logs

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-localserver-logs)

Entity types / item categories

TBD: verify from real items and/or writers

Example items (DocumentClient JSON)

TBD: no example provided yet. Add a sanitized item after verifying from IaC/code or non-prod scan.

Table: codeliver-localserver-sockets

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-localserver-sockets)

Entity types / item categories

TBD: verify from real items and/or writers

Example items (DocumentClient JSON)

TBD: no example provided yet. Add a sanitized item after verifying from IaC/code or non-prod scan.

Table: codeliver-localservers

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-localservers)

Entity types / item categories

localserver heartbeat/config record (per store_id + server_id)

Example items (DocumentClient JSON)

localserver — observed example (sanitized)

```
{
  "store_id": "<STORE_ID>",
  "server_id": "<SERVER_ID>",
  "active": true,
  "addresses": [
    "<PRIVATE_IP>"
  ],
  "appChannel": "<APP_CHANNEL>",
  "automaticBrowserRestart": true,
  "automaticBrowserShow": true,
  "autoScan": false,
  "autoUpdate": true,
  "disks": [
    {
      "_available": 410284785664,
      "_blocks": 499320352768,
      "_capacity": "18%",
      "_filesystem": "Local Fixed Disk",
      "_mounted": "C:",
      "_used": 89035567104
    }
  ],
  "externalIP": "<PUBLIC_IP>",
  "freeMemory": 11592.69140625,
  "group": "<GROUP>",
  "hostname": "<HOSTNAME>",
  "ip": "<PRIVATE_IP>",
  "localserver_logs": false,
  "name": "<LOCALSERVER_NAME>",
  "notifyOffline": false,
  "onlyServer": false,
  "os_arch": "AMD64",
  "platform": "win32",
  "platformRelease": "10.0.22000",
  "platformTime": 1716883360407,
  "platformType": "Windows_NT",
  "port": "4750",
  "pospanel_url": "<POSPANEL_URL>",
  "print_order_images": true,
  "process_arch": "x64",
  "servers_installed": 1,
  "state": "debug",
  "supportAgent": false,
  "systemUptime": 1.1677777777777778,
  "timestamp": "<EPOCH_MS_STRING>",
  "totalMemory": 16163.33203125,
  "updated_timestamp": 1716883360922,
  "update_exists": false,
  "version": "1.0.41",
  "windowsNotifications": true
}
```

Table: codeliver-notifications

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-notifications)

Entity types / item categories

notification (e.g. sms) per group + notification_id

Example items (DocumentClient JSON)

notification — observed example (sanitized + trimmed list)

```
{
  "group": "<GROUP>",
  "notification_id": "<NOTIFICATION_ID>",
  "contents": "<CONTENTS>",
  "delivery_guys_statuses": [
    {
      "delivery_guy_id": "<DELIVERY_GUY_ID_1>",
      "initialized_timestamp": 1759739103050,
      "status": "initialized"
    },
    {
      "delivery_guy_id": "<DELIVERY_GUY_ID_2>",
      "initialized_timestamp": 1759739103050,
      "status": "initialized"
    }
  ],
  "delivery_guy_id": "<DELIVERY_GUY_ID>",
  "device_id": "<DEVICE_ID>",
  "expire": 1760948704,
  "gateway": "<GATEWAY>",
  "group_delivery_guy_id": "<GROUP>_<DELIVERY_GUY_ID>",
  "group_device_id": "<GROUP>_<DEVICE_ID>",
  "headings": "<HEADINGS>",
  "initial_total_completed_estimated_timestamp": 1759739997050,
  "last_recalculation_timestamp": "<EPOCH_MS_STRING>",
  "mobile": "<PHONE>",
  "raw_status": "DELIVERED",
  "reason": "mobileNewRoute",
  "reasonLabel": "<REASON_LABEL>",
  "retry": false,
  "route": "premium",
  "route_id": "<ROUTE_ID>",
  "simulation": true,
  "status": "ignored",
  "system_retry": false,
  "timestamp": "<EPOCH_MS_STRING>",
  "total_completed_estimated_timestamp": 1759739997050,
  "total_distance_km": 3.959,
  "total_requests": 1,
  "total_requests_amount": 5.14,
  "total_tip": 2.79,
  "type": "sms",
  "type_timestamp": "sms_<EPOCH_MS_STRING>",
  "updated_timestamp": 1759739240554
}
```

Table: codeliver-panel-sockets

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-panel-sockets)

Entity types / item categories

websocket session record (panel)

Example items (DocumentClient JSON)

panel socket — observed example (sanitized)

```
{
  "connection": "<CONNECTION_ID>",
  "expire": 1767175049,
  "group": "<GROUP>",
  "sessionID": "<SESSION_ID>",
  "superadmin": true,
  "updated_timestamp": 1767167848572,
  "user_id": "<PANEL_USER_ID>"
}
```

Table: codeliver-panel-users

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-panel-users)

Entity types / item categories

panel user profile

Example items (DocumentClient JSON)

panel user — observed example (sanitized)

```
{
  "group": "<GROUP>",
  "user_id": "<PANEL_USER_ID>",
  "admin": true,
  "allPermissions": true,
  "allPosPermissions": [],
  "language_code": "el",
  "mobile": "<PHONE>",
  "name": null,
  "opensInServerId": "null",
  "password": "<BCRYPT_HASH>",
  "permissions": [
    "*"
  ],
  "allow_panel_pages": [
    "home",
    "requests",
    "control-panel",
    "customers",
    "routes",
    "map",
    "notifications",
    "statistics",
    "charges",
    "delivery-guys",
    "devices",
    "zones",
    "stores",
    "admins-panel",
    "admins-pos",
    "settings"
  ],
  "panel_client_version": "1.8.43",
  "pos": null,
  "posPermissions": [],
  "superadmin": true,
  "updated_timestamp": 1765548957377
}
```

Table: codeliver-pos-sockets

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-pos-sockets)

Entity types / item categories

websocket session record (pos)

Example items (DocumentClient JSON)

pos socket — observed example (sanitized)

```
{
  "connection": "<CONNECTION_ID>",
  "expire": 1767174943,
  "group": "<GROUP>",
  "sessionID": "<SESSION_ID>",
  "store_id": "<STORE_ID>",
  "superadmin": true,
  "updated_timestamp": 1767167743190,
  "user_id": "<POS_USER_ID>"
}
```

Table: codeliver-pos-users

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-pos-users)

Entity types / item categories

pos user profile (per store_id + user_id)

Example items (DocumentClient JSON)

pos user — observed example (sanitized)

```
{
  "store_id": "<STORE_ID>",
  "user_id": "<POS_USER_ID>",
  "admin": true,
  "group": "<GROUP>",
  "language_code": "el",
  "mobile": "<PHONE>",
  "password": "<BCRYPT_HASH>",
  "permissions": [
    "*"
  ],
  "allow_pos_pages": [
    "requests",
    "control-panel",
    "customers",
    "statistics",
    "settings"
  ],
  "pos_client_version": "1.8.44",
  "storeName": "<STORE_NAME>",
  "superadmin": true,
  "updated_timestamp": 1765968912289
}
```

Table: codeliver-requests

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-requests)

Entity types / item categories

request/order record

Example items (DocumentClient JSON)

request — observed example (sanitized)

```
{
    "created_by_user_id": "nikitas_johnchourp_panel",
    "deliveryCost": 0.9,
    "payment_method": "card",
    "lastName": "jjjjjj",
    "delivery_guy_compensation": 0.65,
    "status": "routed",
    "store_address": {
        "addressComments": null,
        "userLng": 22.9747407,
        "formatted_address": "Βοσπόρου 50, Θεσσαλονίκη 544 54, Ελλάδα",
        "doorbellname": null,
        "googleLat": 40.6094519,
        "address_id": "68c4a6a5-b841-4978-8237-5fef29f15381",
        "unverified": false,
        "address_components": {
            "street_number": "50",
            "state": null,
            "user_point_postal_code": null,
            "postal_code": "544 54",
            "city": "Θεσσαλονίκη",
            "street": "Βοσπόρου"
        },
        "floor": null,
        "updated_by_admin": true,
        "googleLng": 22.9747407,
        "userLat": 40.6094519
    },
    "group": "nikitas",
    "storeName": "nikitas_store",
    "initial_arrived_to_store_estimated_timestamp": 1769693785000,
    "nextShortCfRequestId": "A-111",
    "firstName": "jjjj",
    "custom_order_id": null,
    "request_id": "299d23ae-a335-4e54-8c1c-761f20e167f2",
    "storeEmail": null,
    "phone": "6967678686",
    "allow_requests_outside_delivery_areas": false,
    "delivery_area": "Εντός Πόλης",
    "initial_arrived_to_customer_estimated_timestamp": 1769693927000,
    "arrived_to_store_estimated_delay": 0,
    "preparation_time": 3,
    "barcode": {
        "code_set": "B",
        "character_set": "ASCII",
        "check_digit": {
            "value": 36,
            "algorithm": "MOD_103"
        },
        "symbology": "CODE_128",
        "type": "CODE_128",
        "value": "CDL530948420578"
    },
    "request_amount": 0,
    "store_id": "08e9e364-1edd-4d98-840e-da603992470b",
    "group_request_id": "nikitas_299d23ae-a335-4e54-8c1c-761f20e167f2",
    "updated_timestamp": 1769693267980,
    "customer_id": "c7fa23cc-b318-4956-ab90-73bba38d8c16",
    "request_comments": null,
    "address": {
        "userLng": 22.9667821,
        "formatted_address": "Πριάμου 8, Θεσσαλονίκη 544 53, Ελλάδα",
        "doorbellname": null,
        "googleLat": 40.6106294,
        "radius_distance_by_store_id": {
            "08e9e364-1edd-4d98-840e-da603992470b": 0.68
        },
        "isClicked": true,
        "address_id": "5016c5f6-609e-4bd1-ac35-0eb68d92e920",
        "distanceKm": "0.68 km",
        "distanceInStraightLine": 684,
        "address_components": {
            "street_number": "8",
            "state": null,
            "user_point_postal_code": null,
            "postal_code": "544 53",
            "city": "Θεσσαλονίκη",
            "street": "Πριάμου"
        },
        "updated_by_admin": true,
        "googleLng": 22.9667821,
        "userLat": 40.6106294,
        "addressComments": null,
        "zone_id": "2865ee46-86c8-4c80-b70f-4df30a8bbf41",
        "distanceValue": 684,
        "unverified": false,
        "distance_by_store_id": {
            "08e9e364-1edd-4d98-840e-da603992470b": 684
        },
        "floor": null
    },
    "zone_id": "2865ee46-86c8-4c80-b70f-4df30a8bbf41",
    "expire": 1777469268,
    "storePhone": "6980039048",
    "tip": null,
    "uniqueStoreRequestOrderNumber": 19,
    "uniqueRequestOrderNumber": 111,
    "route_id": "219537ab-5453-461b-924d-ddd7ec343350",
    "arrived_to_customer_estimated_timestamp": 1769693927000,
    "delivery_guy_id": "c13969b6-5867-4edc-a0a7-b7a52f8dce3a",
    "routed_timestamp": 1769693267980,
    "last_recalculation_timestamp": 1769693267980,
    "arrived_to_store_estimated_timestamp": 1769693785000,
    "timestamp": "1769690634011"
}
```

Table: codeliver-requests-actions

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-requests-actions)

Entity types / item categories

request action / timeline record

Example items (DocumentClient JSON)

request action — observed example (sanitized)

```
{
  "group_request_id": "<GROUP>_<REQUEST_ID>",
  "timestamp": "<EPOCH_MS_STRING>",
  "expire": 1767449407,
  "group": "<GROUP>",
  "request_id": "<REQUEST_ID>",
  "type": "request_pending"
}
```

Table: codeliver-requests-calculations

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-requests-calculations)

Entity types / item categories

request calculation snapshot record

Example items (DocumentClient JSON)

request calculation — observed example (sanitized)

```
{
  "completed_timestamp": 1767126173871,
  "arrived_to_customer_timestamp": 1767126173871,
  "group_request_id": "<GROUP>_<REQUEST_ID>",
  "route_id": "<ROUTE_ID>",
  "request_id": "<REQUEST_ID>",
  "status": "completed",
  "updated_timestamp": 1767126173871,
  "last_recalculation_timestamp": 1767125678229,
  "group": "<GROUP>",
  "calculation_id": "<CALCULATION_ID>",
  "expire": 1772310174,
  "timestamp": "<EPOCH_MS_STRING>"
}
```

Table: codeliver-routes

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-routes)

Entity types / item categories

route record

Example items (DocumentClient JSON)

route — observed example (sanitized + trimmed lists)

```
{
  "paths_sum": 2,
  "total_requests": 1,
  "route_id": "<ROUTE_ID>",
  "accepted_timestamp": 1767125678229,
  "status": "completed",
  "timestamp": 1767125678349,
  "alerted_delivery_guys": [
    "<DELIVERY_GUY_ID_1>",
    "<DELIVERY_GUY_ID_2>",
    "<DELIVERY_GUY_ID_3>"
  ],
  "last_recalculation_timestamp": "<EPOCH_MS_STRING>",
  "delivery_guy_id": "<DELIVERY_GUY_ID>",
  "delivery_guys_statuses": [
    {
      "accepted_timestamp": 1767125678349,
      "delivery_guy_id": "<DELIVERY_GUY_ID>",
      "status": "accepted",
      "initialized_timestamp": 1767125678349
    }
  ],
  "group": "<GROUP>",
  "simulation": false,
  "total_completed_estimated_timestamp": 1767126938000,
  "initial_total_completed_estimated_timestamp": 1767126317000,
  "completed_timestamp": 1767126173931,
  "total_distance_km": 0,
  "alert_delivery_guys": [],
  "recommended_driver_id": "<DELIVERY_GUY_ID>",
  "total_requests_amount": 0,
  "total_tip": 0,
  "updated_timestamp": 1767126173931
}
```

Table: codeliver-routes-paths

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-routes-paths)

Entity types / item categories

route path record (step within a route)

Example items (DocumentClient JSON)

route path — observed example (sanitized)

```
{
  "arrived_timestamp": 1767125852975,
  "arrived_to_destination_estimated_timestamp": 1767126278000,
  "arrived_user_timestamp": 1767125852975,
  "current_polyline_updated_timestamp": 1767125678229,
  "delivery_guy_id": "<DELIVERY_GUY_ID>",
  "expire": 1772309853,
  "from_coords": {},
  "group": "<GROUP>",
  "simulation": false,
  "last_recalculation_timestamp": 1767125678229,
  "path_type": "delivery_guy_to_store",
  "position": 1,
  "request_id": "<REQUEST_ID>",
  "route_id": "<ROUTE_ID>",
  "route_id_delivery_guy_id": "<ROUTE_ID>_<DELIVERY_GUY_ID>",
  "status": "completed",
  "store_id": "<STORE_ID>",
  "timestamp": "<EPOCH_MS_STRING>",
  "to_coords": {
    "googleLat": 0,
    "googleLng": 0
  },
  "updated_timestamp": 1767125852975,
  "path_id": "<PATH_ID>"
}
```

Table: codeliver-routes-paths-calculations

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-routes-paths-calculations)

Entity types / item categories

route path calculation snapshot record

Example items (DocumentClient JSON)

route path calc — observed example (sanitized)

```
{
  "path_type": "delivery_guy_to_store",
  "path_id": "<PATH_ID>",
  "store_id": "<STORE_ID>",
  "position": 1,
  "from_coords": {},
  "current_polyline_updated_timestamp": 1767125678229,
  "group": "<GROUP>",
  "simulation": false,
  "updated_timestamp": 1767125678229,
  "last_recalculation_timestamp": 1767125678229,
  "arrived_to_destination_estimated_timestamp": 1767126278000,
  "calculation_id": "<CALCULATION_ID>",
  "timestamp": "<EPOCH_MS_STRING>",
  "request_id": "<REQUEST_ID>",
  "route_id": "<ROUTE_ID>",
  "delivery_guy_id": "<DELIVERY_GUY_ID>",
  "route_id_delivery_guy_id": "<ROUTE_ID>_<DELIVERY_GUY_ID>",
  "to_update": false,
  "to_coords": {
    "googleLat": 0,
    "googleLng": 0
  },
  "to_create": true,
  "expire": 1772309678,
  "status": "on_going"
}
```

Table: codeliver-sap-sockets

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-sap-sockets)

Entity types / item categories

websocket session record (sap)

Example items (DocumentClient JSON)

sap socket — observed example (sanitized)

```
{
  "connection": "<CONNECTION_ID>",
  "expire": 1767175425,
  "superadmin_id": "<SAP_SUPERADMIN_ID>",
  "updated_timestamp": 1767168225044
}
```

Table: codeliver-sap-users

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-sap-users)

Entity types / item categories

sap user profile

Example items (DocumentClient JSON)

sap user — observed example (sanitized)

```
{
  "superadmin_id": "<SAP_SUPERADMIN_ID>",
  "admin": true,
  "groups": [
    "*"
  ],
  "language_code": "el",
  "mobile": "<PHONE>",
  "password": "<BCRYPT_HASH>",
  "permissions": [
    "*"
  ],
  "superadmin": true,
  "sap_client_version": "2.2.17",
  "updated_timestamp": 1767168225044
}
```

Table: codeliver-store-charges

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-store-charges)

Entity types / item categories

charge record / billing event

Example items (DocumentClient JSON)

store charge — observed example (sanitized)

```
{
  "group": "<GROUP>",
  "timestamp": "<EPOCH_MS_STRING>",
  "amount": "0.035",
  "expire": 1827731419,
  "newBalance": "-0.28",
  "partner_id": "<PARTNER_ID>",
  "quantity": 1,
  "reason": "mobileRemindPassword",
  "reasonLabel": "<REASON_LABEL>",
  "type": "sms",
  "updated_timestamp": 1764659418987
}
```

Table: codeliver-stores

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (codeliver-stores)

Entity types / item categories

store profile/config

Example items (DocumentClient JSON)

store — observed example (sanitized)

```
{
  "group": "<GROUP>",
  "store_id": "<STORE_ID>",
  "addresses": [
    {
      "addressComments": null,
      "address_components": {
        "city": "<CITY>",
        "postal_code": "<POSTAL_CODE>",
        "state": null,
        "street": "<STREET>",
        "street_number": "<STREET_NUMBER>",
        "user_point_postal_code": null
      },
      "address_id": "<ADDRESS_ID>",
      "doorbellname": null,
      "floor": null,
      "formatted_address": "<FORMATTED_ADDRESS>",
      "googleLat": 0,
      "googleLng": 0,
      "unverified": false,
      "updated_by_admin": true,
      "userLat": 0,
      "userLng": 0
    }
  ],
  "area": "<AREA>",
  "balance": -0.035,
  "delivery_areas": [],
  "email": null,
  "invoices": [],
  "last_short_cf_request_id": 1,
  "mobile": "<PHONE>",
  "phone": "<PHONE>",
  "storeDeactivated": false,
  "storeName": "<STORE_NAME>",
  "storename": null,
  "third_party_store": true,
  "uniqueRequestOrderNumber": 0,
  "updated_timestamp": 1767021500440,
  "use_zone_delivery_areas": true,
  "zone_id": "<ZONE_ID>"
}
```

Table: google-api-counter

Source of truth

Keys & indexes: .codex/playbooks/codeliver-dynamodb-keys-and-indexes.md (google-api-counter)

NOTE: Keys are TBD: verify from IaC in the keys playbook (do not infer).

Entity types / item categories

api usage counter record (verify discriminator/strategy from writers)

Example items (DocumentClient JSON)

counter — observed example (sanitized)

```
{
  "apikey-date": "<GOOGLE_API_KEY>-<DATE_DD/MM/YYYY>",
  "counter": 44
}
```
