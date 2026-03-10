# AGENTS.md

<INSTRUCTIONS>
Global guidance for Codex assistance (CodeDeliver)

You are assisting on the CodeDeliver codebase (lambdas + projects). Your outputs must be grounded in the repository code and must include actionable steps.

## Canonical .codex guidance (DO NOT DUPLICATE)

This file and the playbooks are **workspace-global** and must remain **single-source-of-truth**:

- Canonical instructions file:
  - `.codex/AGENTS.md` (this file)
- Canonical playbooks directory:
  - `.codex/playbooks/`

Rules:

- **Do NOT create or copy** `AGENTS.md` into any repo, lambda folder, or project folder.
- If a repo needs to reference guidance, **link to the canonical `.codex/…` path** instead of duplicating content.
- If the user asks to "update/add/change `AGENTS.md`", interpret it as **only** `.codex/AGENTS.md` (this file), and do not edit any other `AGENTS.md` path.

## CodeDeliver reference playbooks (canonical, global)

- DynamoDB table keys (PK/SK/Indexes):
  - `.codex/playbooks/codeliver-dynamodb-keys-and-indexes.md`

- DynamoDB table lambda triggers:
  - `.codex/playbooks/codeliver-dynamodb-lambda-triggers.md`

- DynamoDB table Kinesis triggers:
  - `.codex/playbooks/codeliver-dynamodb-kinesis-triggers.md`

- DynamoDB item shapes & examples (attributes beyond keys/indexes):
  - `.codex/playbooks/codeliver-dynamodb-item-examples.md`

- SQS queue configurations (df account, codeliver-\*):
  - `.codex/playbooks/codeliver-sqs-queues.md`

- API Gateway configurations (df account, codeliver-\*):
  - `.codex/playbooks/codeliver-api-gateways.md`

- S3 bucket configurations (df account, codeliver-\*):
  - `.codex/playbooks/codeliver-s3.md`

- EventBridge configurations (df account, codeliver-\*):
  - `.codex/playbooks/codeliver-amazon-event-bridges.md`

- CloudFront configurations (df account, codeliver-\*):
  - `.codex/playbooks/codeliver-amazon-cloudfronts.md`

Rules:

- Never guess DynamoDB PK/SK/GSI/LSI attribute names or types.
- For requests/routes/route_paths (and any other items documented there), always consult `.codex/playbooks/codeliver-dynamodb-item-examples.md` for attribute shapes before using/adding fields.

## 0) Terminology & local workspace assumptions (always)

- When the user says **“a lambda” / “lambda function”**, assume the code is **already downloaded locally** and lives under:
  - `/home/dm-soft-1/Downloads/lambdas`
- When the user says **“a project”** (frontend/backend/tool), assume the code is **already downloaded locally** and lives under:
  - `/home/dm-soft-1/Downloads/projects`
- When the user says **“a component”** (Angular/Ionic component/page/screen/module/service/feature in a project), assume it is **already downloaded locally** and lives under:
  - `/home/dm-soft-1/Downloads/projects`
    and treat it as an **end-to-end entry point**:
  - You MUST automatically search for **all lambdas used/triggered by the component** (directly or indirectly).
  - You MUST automatically trace the **connections from those lambdas to other lambdas/resources** (topics/queues/EventBridge rules/tables/buckets/routes) to perform impact analysis (direct + 1-hop downstream). By default, provide a concise impact summary in the reply, not an integration map.
- Assume **lambdas and projects are connected** (shared models, API clients, auth flows, events, topics/queues, tables, routes). You may freely scan **both** roots to trace end-to-end flows and identify bugs.
- Assume **all lambdas and projects you can discover under the two roots are already downloaded on the user’s PC** (even if the user didn’t mention them). Do not ask the user to confirm existence—**enumerate/search** as needed.
- Assume **codeliver-app runs on iOS, Android, and Web**, so changes must be cross-platform safe (native + browser).
- For changes that affect socket-emitter queue behavior (grouping/chunking/dedup for panel/pos/app/sap queues), also consult and update:
  - `/home/dm-soft-1/Downloads/lambdas/codeliver_all/dm-codeliver-brain/docs/system/README.md`
- If the above local paths are **not accessible** in the current execution environment, explicitly say so and provide the **exact commands** the user should run locally (and what output to paste back).

## 0.0) Authorizer claims (CodeDeliver)

- **SAP** authorizer exposes only `superadmin_id` (no `group`). The JWT is signed with `{ id: superadmin_id }` in `lambdas/codeliver_all/codeliver-sap-login`, so group must be provided in request bodies when needed.
- **Panel** authorizer exposes `user_id` and `group` (JWT signed with `{ id: user_id, group }` in `lambdas/codeliver_all/codeliver-panel-login`).
- **POS** authorizer exposes `user_id`, `store_id`, `group` (JWT signed with `{ id: user_id, store_id, group }` in `lambdas/codeliver_all/codeliver-pos-login`).
- **App** authorizer exposes `device_id`, `delivery_guy_id`, `group` (JWT signed with `{ id: device_id, delivery_guy_id, group }` in `lambdas/codeliver_all/codeliver-app-login-mobile-pin` and `lambdas/codeliver_all/codeliver-app-device-login`).

## 0.1) Cross-project parity rules (Admins panel)

- Keep these components/lambdas in **lockstep**; when changing one side, **apply the same UI/logic changes to the other** (including HTML/SCSS/global classes and backend validation/behavior):
  - `projects/codeliver/codeliver-panel/src/app/administration/admins-panel/AdminsPanelPage`
  - `projects/codeliver/codeliver-panel/src/app/administration/admins-panel/admin-panel/AdminPanelComponent`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/create-admin-panel-modal/CreateAdminPanelModalComponent`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/edit-admin-panel-modal/EditAdminPanelModalComponent`
  - `projects/codeliver/codeliver-sap/src/app/shared/modals/show-group-admins-panel-modal/ShowGroupAdminsPanelModalComponent`
  - `projects/codeliver/codeliver-sap/src/app/shared/modals/show-group-admins-panel-modal/admin-panel/AdminPanelComponent`
  - `projects/codeliver/codeliver-sap/src/app/shared/modals/create-admin-panel-modal/CreateAdminPanelModalComponent`
  - `projects/codeliver/codeliver-sap/src/app/shared/modals/edit-admin-panel-modal/EditAdminPanelModalComponent`
  - `lambdas/codeliver_all/codeliver-panel-handle-panel-user` ↔ `lambdas/codeliver_all/codeliver-sap-handle-panel-user`
  - `lambdas/codeliver_all/codeliver-panel-fetch-panel-users` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-panel-users`
  - `lambdas/codeliver_all/codeliver-panel-fetch-users-sockets` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-panel-users-sockets`

## 0.2) Cross-project parity rules (Admins POS users)

- Keep these components/lambdas in **lockstep**; when changing one side, **apply the same UI/logic changes to the other** (including HTML/SCSS/global classes and backend validation/behavior):
  - `projects/codeliver/codeliver-panel/src/app/administration/admins-pos/AdminsPosPage`
  - `projects/codeliver/codeliver-panel/src/app/administration/admins-pos/admin-pos/AdminPosComponent`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/create-admin-pos-modal/CreateAdminPosModalComponent`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/edit-admin-pos-modal/EditAdminPosModalComponent`
  - `projects/codeliver/codeliver-sap/src/app/shared/modals/show-group-admins-pos-modal/ShowGroupAdminsPosModalComponent`
  - `projects/codeliver/codeliver-sap/src/app/shared/modals/show-group-admins-pos-modal/admin-pos/AdminPosComponent`
  - `projects/codeliver/codeliver-sap/src/app/shared/modals/create-admin-pos-modal/CreateAdminPosModalComponent`
  - `projects/codeliver/codeliver-sap/src/app/shared/modals/edit-admin-pos-modal/EditAdminPosModalComponent`
  - `lambdas/codeliver_all/codeliver-panel-handle-pos-user` ↔ `lambdas/codeliver_all/codeliver-sap-handle-pos-user`
  - `lambdas/codeliver_all/codeliver-panel-fetch-pos-users` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-pos-users`
  - `lambdas/codeliver_all/codeliver-panel-fetch-pos-users-sockets` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-pos-users-sockets`

## 0.3) Cross-project parity rules (Zones)

- Keep these components/lambdas in **lockstep**; οποιαδήποτε μελλοντική αλλαγή στο `projects/codeliver/codeliver-panel` για Zones πρέπει να μεταφέρεται ισοδύναμα στο `projects/codeliver/codeliver-sap` (UI/logic, HTML/SCSS/global classes και backend validation/behavior):
  - `projects/codeliver/codeliver-panel/src/app/map-zones-and-stores/zones/zones.page.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-group-zones-modal/show-group-zones-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/common/zone-item/zone-item.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/common/zone-item/zone-item.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/create-zone-modal/create-zone-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/create-zone-modal/create-zone-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/edit-zone-modal/edit-zone-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/edit-zone-modal/edit-zone-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-delivery-guys-info-modal/show-delivery-guys-info-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-delivery-guys-info-modal/show-delivery-guys-info-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-info-modal/show-info-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-info-modal/show-info-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/delivery-area-store-costs-modal/delivery-area-store-costs-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/delivery-area-store-costs-modal/delivery-area-store-costs-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-delivery-guy-period-path-modal/show-delivery-guy-period-path-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-delivery-guy-period-path-modal/show-delivery-guy-period-path-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-delivery-guy-map-modal/show-delivery-guy-map-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-delivery-guy-map-modal/show-delivery-guy-map-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/common/show-lottie-group-plans-information/show-lottie-group-plans-information.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/common/show-lottie-group-plans-information/show-lottie-group-plans-information.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-real-coords-history-modal/show-real-coords-history-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-real-coords-history-modal/show-real-coords-history-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-reports-modal/show-reports-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-reports-modal/show-reports-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/edit-delivery-guy-modal/edit-delivery-guy-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/edit-delivery-guy-modal/edit-delivery-guy-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/select-delivery-guy-stores-ignore-list-modal/select-delivery-guy-stores-ignore-list-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/select-delivery-guy-stores-ignore-list-modal/select-delivery-guy-stores-ignore-list-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/create-zone-delivery-areas-modal/create-zone-delivery-areas-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/create-zone-delivery-areas-modal/create-zone-delivery-areas-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/edit-delivery-area-settings-modal/edit-delivery-area-settings-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/edit-delivery-area-settings-modal/edit-delivery-area-settings-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-delivery-guy-status-history-modal/show-delivery-guy-status-history-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-delivery-guy-status-history-modal/show-delivery-guy-status-history-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/edit-delivery-area-schedule-modal/edit-delivery-area-schedule-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/edit-delivery-area-schedule-modal/edit-delivery-area-schedule-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/delivery-guys-and-devices/delivery-guys/delivery-guy/delivery-guy.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/delivery-guys-and-devices/delivery-guys/delivery-guy/delivery-guy.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/edit-device-modal/edit-device-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/edit-device-modal/edit-device-modal.component.ts`
  - `lambdas/codeliver_all/codeliver-panel-handle-device` ↔ `lambdas/codeliver_all/codeliver-sap-handle-device`
  - `lambdas/codeliver_all/codeliver-panel-handle-delivery-guy` ↔ `lambdas/codeliver_all/codeliver-sap-handle-delivery-guy`
  - `lambdas/codeliver_all/codeliver-panel-handle-group-zone` ↔ `lambdas/codeliver_all/codeliver-sap-handle-zone`
  - `lambdas/codeliver_all/codeliver-panel-fetch-group-zones` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-zones`
  - `lambdas/codeliver_all/codeliver-panel-reorder-zones` ↔ `lambdas/codeliver_all/codeliver-sap-reorder-zones`
  - `lambdas/codeliver_all/codeliver-panel-fetch-group-stores` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-stores`
  - `lambdas/codeliver_all/codeliver-panel-fetch-delivery-guys` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-delivery-guys`
  - `lambdas/codeliver_all/codeliver-panel-device-send-cloud-command` ↔ `lambdas/codeliver_all/codeliver-sap-device-send-cloud-command`
  - `lambdas/codeliver_all/codeliver-panel-fetch-delivery-guys-actions` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-delivery-guys-actions`
  - `lambdas/codeliver_all/codeliver-fetch-delivery-guy-raw-coordinates` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-delivery-guy-raw-coordinates`
  - `lambdas/codeliver_all/codeliver-panel-fetch-delivery-guy-path` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-delivery-guy-path`
  - `lambdas/codeliver_all/codeliver-panel-handle-delivery-guy-shift` ↔ `lambdas/codeliver_all/codeliver-sap-handle-delivery-guy-shift`
  - `lambdas/codeliver_all/codeliver-panel-fetch-batches` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-batches`
  - `lambdas/codeliver_all/codeliver-panel-fetch-devices` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-delivery-devices`

## 0.4) Cross-project parity rules (Devices)

- Keep these components/lambdas in **lockstep**; οποιαδήποτε μελλοντική αλλαγή στο `projects/codeliver/codeliver-panel` σχετικά με Devices πρέπει να μεταφέρεται ισοδύναμα στο `projects/codeliver/codeliver-sap` (UI/logic, HTML/SCSS/global classes και backend validation/behavior):
  - `projects/codeliver/codeliver-panel/src/app/delivery-guys-and-devices/devices/devices.page.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-group-devices-modal/show-group-devices-modal.component.ts` (parity entry-point)
  - `projects/codeliver/codeliver-panel/src/app/delivery-guys-and-devices/devices/devices-item/devices-item.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-group-devices-modal/devices-item/devices-item.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/create-device-modal/create-device-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/create-device-modal/create-device-modal.component.ts`
  - `lambdas/codeliver_all/codeliver-panel-fetch-delivery-guys` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-delivery-guys`
  - `lambdas/codeliver_all/codeliver-panel-fetch-devices` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-delivery-devices`
  - `lambdas/codeliver_all/codeliver-panel-fetch-devices-sockets` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-delivery-devices-sockets`
  - `lambdas/codeliver_all/codeliver-panel-fetch-group-zones` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-zones`

## 0.5) Cross-project parity rules (Delivery Guys)

- Keep these components/lambdas in **lockstep**; οποιαδήποτε μελλοντική αλλαγή στο `projects/codeliver/codeliver-panel` σχετικά με Delivery Guys πρέπει να μεταφέρεται ισοδύναμα στο `projects/codeliver/codeliver-sap` (UI/logic, HTML/SCSS/global classes και backend validation/behavior):
  - `projects/codeliver/codeliver-panel/src/app/delivery-guys-and-devices/delivery-guys/delivery-guys.page.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-group-delivery-guys-modal/show-group-delivery-guys-modal.component.ts` (parity entry-point)
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/edit-device-modal/edit-device-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/edit-device-modal/edit-device-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-delivery-guy-status-history-modal/show-delivery-guy-status-history-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-delivery-guy-status-history-modal/show-delivery-guy-status-history-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-real-coords-history-modal/show-real-coords-history-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-real-coords-history-modal/show-real-coords-history-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-delivery-guy-map-modal/show-delivery-guy-map-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-delivery-guy-map-modal/show-delivery-guy-map-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/edit-delivery-guy-modal/edit-delivery-guy-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/edit-delivery-guy-modal/edit-delivery-guy-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/create-delivery-guy-modal/create-delivery-guy-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/create-delivery-guy-modal/create-delivery-guy-modal.component.ts`
  - `lambdas/codeliver_all/codeliver-panel-fetch-devices-sockets` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-delivery-devices-sockets`
  - `lambdas/codeliver_all/codeliver-panel-fetch-devices` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-delivery-devices`
  - `lambdas/codeliver_all/codeliver-panel-reorder-delivery-guys` ↔ `lambdas/codeliver_all/codeliver-sap-reorder-delivery-guys`
  - `lambdas/codeliver_all/codeliver-panel-fetch-group-zones` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-zones`
  - `lambdas/codeliver_all/codeliver-panel-fetch-delivery-guys` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-delivery-guys`

## 0.6) Cross-project parity rules (Stores)

- Keep these components/lambdas in **lockstep**; οποιαδήποτε μελλοντική αλλαγή στο `projects/codeliver/codeliver-panel` σχετικά με Stores πρέπει να μεταφέρεται ισοδύναμα στο `projects/codeliver/codeliver-sap` (UI/logic, HTML/SCSS/global classes και backend validation/behavior):
  - `projects/codeliver/codeliver-panel/src/app/map-zones-and-stores/stores/stores.page.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-group-stores-modal/show-group-stores-modal.component.ts` (parity entry-point)
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/edit-store-modal/edit-store-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/edit-store-modal/edit-store-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-info-modal/show-info-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-info-modal/show-info-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/edit-map-marker-modal/edit-map-marker-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/edit-map-marker-modal/edit-map-marker-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/select-address-modal/select-address-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/select-address-modal/select-address-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/edit-store-information-modal/edit-store-information-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/edit-store-information-modal/edit-store-information-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/create-store-delivery-areas-modal/create-store-delivery-areas-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/create-store-delivery-areas-modal/create-store-delivery-areas-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/select-zone-modal/select-zone-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/select-zone-modal/select-zone-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/create-store-modal/create-store-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/create-store-modal/create-store-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/map-zones-and-stores/stores/store-item/store-item.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-group-stores-modal/store-item/store-item.component.ts`
  - `lambdas/codeliver_all/codeliver-panel-fetch-group-stores` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-stores`
  - `lambdas/codeliver_all/codeliver-panel-fetch-group-zones` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-zones`
  - `lambdas/codeliver_all/codeliver-panel-reorder-stores` ↔ `lambdas/codeliver_all/codeliver-sap-reorder-stores`
  - `lambdas/codeliver_all/codeliver-panel-handle-group-zone` ↔ `lambdas/codeliver_all/codeliver-sap-handle-zone`
  - `lambdas/codeliver_all/codeliver-panel-handle-store` ↔ `lambdas/codeliver_all/codeliver-sap-handle-store`

## 0.7) Cross-project parity rules (Requests Route Map: Panel ↔ POS)

- Keep these components in **lockstep** between `projects/codeliver/codeliver-panel` and `projects/codeliver/codeliver-pos` for route-map modal opening logic and UI behavior:
  - `projects/codeliver/codeliver-panel/src/app/shared/common/request-item/request-item.component.ts` ↔ `projects/codeliver/codeliver-pos/src/app/shared/common/request-item/request-item.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/common/request-item/request-item.component.html` ↔ `projects/codeliver/codeliver-pos/src/app/shared/common/request-item/request-item.component.html`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-route-routed-without-delivery-guy-id-map-modal/show-route-routed-without-delivery-guy-id-map-modal.component.ts` ↔ `projects/codeliver/codeliver-pos/src/app/shared/modals/show-route-routed-without-delivery-guy-id-map-modal/show-route-routed-without-delivery-guy-id-map-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-route-routed-without-delivery-guy-id-map-modal/show-route-routed-without-delivery-guy-id-map-modal.component.html` ↔ `projects/codeliver/codeliver-pos/src/app/shared/modals/show-route-routed-without-delivery-guy-id-map-modal/show-route-routed-without-delivery-guy-id-map-modal.component.html`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-route-routed-without-delivery-guy-id-map-modal/show-route-routed-without-delivery-guy-id-map-modal.component.scss` ↔ `projects/codeliver/codeliver-pos/src/app/shared/modals/show-route-routed-without-delivery-guy-id-map-modal/show-route-routed-without-delivery-guy-id-map-modal.component.scss`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-route-routed-with-delivery-guy-id-map-modal/show-route-routed-with-delivery-guy-id-map-modal.component.ts` ↔ `projects/codeliver/codeliver-pos/src/app/shared/modals/show-route-routed-with-delivery-guy-id-map-modal/show-route-routed-with-delivery-guy-id-map-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-route-routed-with-delivery-guy-id-map-modal/show-route-routed-with-delivery-guy-id-map-modal.component.html` ↔ `projects/codeliver/codeliver-pos/src/app/shared/modals/show-route-routed-with-delivery-guy-id-map-modal/show-route-routed-with-delivery-guy-id-map-modal.component.html`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-route-routed-with-delivery-guy-id-map-modal/show-route-routed-with-delivery-guy-id-map-modal.component.scss` ↔ `projects/codeliver/codeliver-pos/src/app/shared/modals/show-route-routed-with-delivery-guy-id-map-modal/show-route-routed-with-delivery-guy-id-map-modal.component.scss`

- `openShowRouteModal` must use only these two modal targets:
  - `ShowRequestRoutedWithoutDeliveryGuyIdMapModalComponent`
  - `ShowRequestRoutedWithDeliveryGuyIdMapModalComponent`

- Do **not** re-introduce or use the legacy modal trio in `openShowRouteModal`:
  - `ShowRouteActiveMapModalComponent`
  - `ShowRouteRoutedMapModalComponent`
  - `ShowRouteCompletedMapModalComponent`

## 0.8) Cross-project parity rules (Control Panel: Panel ↔ SAP)

- Keep these components/lambdas in **lockstep** between `projects/codeliver/codeliver-panel` and `projects/codeliver/codeliver-sap` for Control Panel behavior (UI/logic, HTML/SCSS/global classes and backend validation/behavior):
  - `projects/codeliver/codeliver-panel/src/app/control-panel/control-panel.page.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-group-control-panel-modal/show-group-control-panel-modal.component.ts` (parity entry-point)
  - `projects/codeliver/codeliver-panel/src/app/control-panel/control-panel.page.html` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-group-control-panel-modal/show-group-control-panel-modal.component.html`
  - `projects/codeliver/codeliver-panel/src/app/control-panel/control-panel.page.scss` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-group-control-panel-modal/show-group-control-panel-modal.component.scss`
  - `projects/codeliver/codeliver-panel/src/app/shared/common/map-route-requests-info-cards/map-route-requests-info-cards.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/common/map-route-requests-info-cards/map-route-requests-info-cards.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/common/map-route-requests-info-cards/map-route-requests-info-cards.component.html` ↔ `projects/codeliver/codeliver-sap/src/app/shared/common/map-route-requests-info-cards/map-route-requests-info-cards.component.html`
  - `projects/codeliver/codeliver-panel/src/app/shared/common/map-route-requests-info-cards/map-route-requests-info-cards.component.scss` ↔ `projects/codeliver/codeliver-sap/src/app/shared/common/map-route-requests-info-cards/map-route-requests-info-cards.component.scss`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-route-active-map-info-modal/show-route-active-map-info-modal.component.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-route-active-map-info-modal/show-route-active-map-info-modal.component.ts`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-route-active-map-info-modal/show-route-active-map-info-modal.component.html` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-route-active-map-info-modal/show-route-active-map-info-modal.component.html`
  - `projects/codeliver/codeliver-panel/src/app/shared/modals/show-route-active-map-info-modal/show-route-active-map-info-modal.component.scss` ↔ `projects/codeliver/codeliver-sap/src/app/shared/modals/show-route-active-map-info-modal/show-route-active-map-info-modal.component.scss`
  - `projects/codeliver/codeliver-panel/src/app/shared/utils/route-path-map-overlays.util.ts` ↔ `projects/codeliver/codeliver-sap/src/app/shared/utils/route-path-map-overlays.util.ts`
  - `lambdas/codeliver_all/codeliver-panel-fetch-routes` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-routes`
  - `lambdas/codeliver_all/codeliver-panel-fetch-routes-paths` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-routes-paths`
  - `lambdas/codeliver_all/codeliver-panel-handle-route` ↔ `lambdas/codeliver_all/codeliver-sap-handle-route`
  - `lambdas/codeliver_all/codeliver-panel-fetch-delivery-requests` ↔ `lambdas/codeliver_all/codeliver-sap-fetch-delivery-requests` (route-id mode parity)

## 1) Output style & working rules (always)

- Keep replies concise and actionable.
- Always respond in Greek, regardless of the language used by the user.
- Always write implementation plans in Greek (including the plan you intend to execute).
- Prefer minimal, style-consistent changes; avoid large refactors unless explicitly requested.
- When changes are needed in files under `ios/` or `android/` (regenerated on deploy), do **not** edit those files directly. Create/update a script (e.g., `build-before.js`, `build-after.js`, `capacitor-project.ts`) that applies the changes during build/deploy.
- **Default mode autonomy (mandatory):** when **not** in Plan Mode, do **not** ask clarifying questions. Proceed autonomously with the best implementation and recommendations based on repository context and reasonable assumptions.
- **Parity confirmation gate (mandatory):** before applying any cross-project sync/parity change, ask first whether parity is required and exactly which target project(s) must be kept in lockstep (e.g. `panel`, `sap`, `pos`, `app`).
  - If the user requests scoped work (e.g. `sap-only` or `panel-only`), implement only that scope and state it explicitly as a parity exception in the response.
- **Credentialed AWS access policy (mandatory):**
  - Do not run AWS API calls using user credentials (DynamoDB, S3, SQS, SNS, Lambda, CloudWatch, STS, etc.) unless the user explicitly requests it in the current prompt.
  - Approval is single-request only and does not persist to subsequent prompts.
  - If explicit request is missing, provide exact commands for the user to run locally instead of executing with credentials.
- Ask clarifying questions only in Plan Mode (via interactive options UI) or when execution is blocked by a truly mandatory user decision that cannot be inferred from code/context.
- **Build persistence rule (mandatory):** when the user asks to run a build/install, keep iterating (`run -> inspect error -> apply fix -> rerun`) until it succeeds or a hard external blocker appears. For Android `installDebug`, if `INSTALL_FAILED_UPDATE_INCOMPATIBLE` appears, uninstall the existing app package from the device and retry install.
  - Do not run AWS API calls using user credentials (DynamoDB, S3, SQS, SNS, Lambda, CloudWatch, STS, etc.) unless the user explicitly requests it in the current prompt.
- **Re-entrant pending-selection safety (mandatory):** when implementing any pending UI selection flow that opens map markers/info windows (or any handler that can trigger state refresh), always apply `clear-before-open` and `restore-on-miss`.
  - Required pattern: copy pending id locally -> set pending state to `null` -> attempt selection/open -> if selection target is missing, restore pending id.
  - Forbidden pattern: clearing pending id only after `open...()`/selection handler returns, because those handlers may synchronously trigger refresh cycles and re-enter the pending-flush method, causing recursion and stack overflows.
  - Quick self-check: verify no cycle of the form `flushPending* -> open/select* -> refresh* -> flushPending*` can run with the same pending id still set.
- **Plan Mode question UX (mandatory):** when in Plan Mode, ask clarifying questions through the interactive options UI (`request_user_input`) and avoid posting free-form question lists in plain chat. Keep asking through the interactive UI until required decisions are collected, then present the final plan so the user can choose “Implement Plan”.
### MCP Smart Routing (Playwright / Figma / Notion / Linear)

- **Auto-first policy (mandatory):** in non-Plan mode, automatically select and use the most relevant MCP server among `playwright`, `figma`, `notion`, `linear` when the user intent clearly matches one of them; do not ask permission first.
- **Trigger matrix (mandatory):**
  - `playwright`: browser automation, UI bug reproduction, screenshots/snapshots, form flows, regressions, real-page interaction debugging.
  - `figma`: Figma links/node IDs, design-to-code, visual parity checks, extracting design context/assets/variables.
  - `notion`: knowledge capture, documentation, FAQ/how-to pages, decision logs, research synthesis into Notion.
  - `linear`: issue/project/cycle/label/status workflows in Linear.
- **PM conflict policy (mandatory):** `ClickUp` remains primary baseline for CodeDeliver task workflow. Use `linear` as secondary only when the user explicitly asks for Linear, or when the context is clearly a Linear workspace workflow.
- **Fallback policy (mandatory):** if an MCP server is unavailable or auth fails, continue with the best non-blocking fallback flow and provide exact setup/login commands only when needed.
  - `notion`: `codex mcp add notion --url https://mcp.notion.com/mcp` then `codex mcp login notion`
  - `linear`: `codex mcp add linear --url https://mcp.linear.app/mcp` then `codex mcp login linear`
  - `figma`: add in `~/.codex/config.toml`:
    - `[mcp_servers.figma]`
    - `url = "https://mcp.figma.com/mcp"`
    - `bearer_token_env_var = "FIGMA_OAUTH_TOKEN"`
    - `http_headers = { "X-Figma-Region" = "us-east-1" }`
  - verify MCP availability with `codex mcp list` (and restart Codex after auth/config changes).
- **Guardrails (mandatory):**
  - Do not force MCP usage when it does not materially improve the task.
  - Do not invent data from `notion`/`linear`/`figma` when access is missing; state the limitation explicitly.
  - Keep tool usage minimal and justify MCP choice briefly in progress updates.
- **CodeDeliver examples (reference):**
  - Prompt like `βρες γιατί δεν ανοίγει modal στο sap` -> prefer `playwright` first for reproduction and UI-state evidence.
  - Prompt with Figma URL for SAP/Panel modal parity -> prefer `figma` first, then implement with existing project conventions.
  - Prompt like `γράψε doc/faq για τη ροή` -> prefer `notion` for structured capture (unless user asks local markdown only).
  - Prompt like `φτιάξε/update issue` -> keep `ClickUp` baseline; use `linear` only when explicitly requested or clearly required by workspace context.
- Before changing any lambda, review `.codex/AGENTS.md` and the relevant `.codex/refs/codeliver-*-lambdas.md` reference files to confirm required inputs/examples so the flow does not break.
- Always end replies with links to the files you touched so they can be opened directly in VS Code.
- Always run `ionic build` after each change batch only when you changed files under `projects/`; fix any build errors until it succeeds. If no project files changed (docs/lambdas/.codex), do not run it.
- Translation rule (UI text in templates): never hardcode user-visible labels/messages/statuses (including Greek text such as `ενεργο` / `ανενεργο`) directly in templates. Always use the translate pipe with a key (e.g., `{{ "store-status-active" | translate }}`) and add/update that key in **every** `src/assets/i18n/*.json` language file.
- Translation completion gate (mandatory): for every change that adds/updates translation key usage (`| translate`, `translate.instant`, `translate.get`, `translate.stream`), run a key-coverage check against all `src/assets/i18n/*.json` files of the impacted frontend project before completing the task.
  - If any used key is missing from at least one locale file, the task is **not complete**.
  - Final reply must include: (a) the checked key set, and (b) the locale files where keys were added/updated.
- Translation key safety: do not introduce dotted translation keys that collide with existing **string** keys (e.g. avoid `statistics.week-grouping-hint` if `statistics` is already a string). Prefer flat keys like `statistics-week-grouping-hint`, or ensure the parent key is an object in all locales.
- UI affordance rule (chips): do **not** render `ion-chip` elements that look clickable but perform no action on tap/click. If the content is informational only, use `ion-badge`, `ion-text`, `ion-label`, or plain text containers instead.
- CustomError translation coverage (frontend-facing): when adding/changing any `CustomError` code in a lambda that is frontend-reachable (directly called by frontend, or one-hop downstream from a frontend-called lambda and its result is returned to frontend), you MUST ensure translation coverage in impacted frontend project(s) for **all** `src/assets/i18n/*.json` files.
  - Frontend-visible error fields are `comment_id` and `comments`.
  - Caller-based path policy:
    - Use nested keys `lambdas_responses.<caller_lambda>.<error_code>` when the frontend caller path uses `presentPostFailureAlert(..., "<caller_lambda>")` or `lambdas_responses.<caller_lambda>.`.
    - Use root key `<error_code>` when the frontend caller path translates `res.comment_id` / `res?.comment_id` directly.
  - For unresolved lambda mapping from refs, treat as warn+skip (do not block unrelated work), but report them explicitly.
- Logging: when dumping events for troubleshooting, do not redact `event.body`; keep it intact while still redacting auth tokens, cookies, and passwords.
- **Clarity over efficiency:** if there is a trade-off between performance and readability/maintainability, prefer the simplest correct implementation (even if it is less efficient)
- avoid `ng-template`/`ngTemplateOutlet`, keep the full markup inline inside each `@for` loop, even if it duplicates markup.
- In Angular templates, prefer the new control flow blocks; use `@if`/`@for` and avoid `*ngIf`/`*ngFor`.
- Ionic modal safety rule (componentProps vs signals): values passed through `modalController.create({ componentProps: ... })` are assigned directly on the component instance. Do **not** model those props as callable signal inputs (`input()` / `InputSignal`) unless callers pass signals explicitly. For primitive/array/object props (e.g. `mode`, `title`, `items`), use plain `@Input()` properties; otherwise runtime errors like `TypeError: this.<prop> is not a function` can occur.
- **Dependency hygiene (always):** remove unused dependencies from `package.json`; do not keep deps “just in case”.
- **Node.js Lambda rules (always):** apply these requirements for any Node.js Lambda change (not only harden flows):
  - **Null-safe optional fields:** when reading fields from DynamoDB/API results that may be missing, always use optional chaining or explicit guards (e.g. `request?.readyToPickUp`, `request?.status`) to prevent runtime `TypeError` from `undefined` values.
  - **AWS SDK v3 deps in Lambdas**: remove `@aws-sdk/*` from Lambda `package.json` (and update `package-lock.json`) even if imported, because the execution environment guarantees AWS SDK v3 availability at runtime.
    - If a repo still contains `@aws-sdk/*` for non-Lambda reasons, do **not** version-pin them in `package.json` (prefer semver ranges like `^`) and remove any unused ones.
  - **Deploy scripts must be canonical**: ensure scripts exist (rewrite legacy `zsh -ic 'lu'` wrappers to these):
    - `deploy:prod`: `lambda-upload deploy-prod df`
    - `deploy:prod:check`: `lambda-upload deploy-prod df --check --force --assume-runtime nodejs24.x`
    - `deploy:prod:upgrade`: `lambda-upload deploy-prod df --upgrade-config`
  - **Legacy callback handlers must be removed**: migrate handlers from the legacy callback style (`(event, context, callback)` + `callback(...)`) to `async`/`await` with `return`/`throw`.
    - Do **not** keep mixed signatures like `async (event, context, callback)`; treat this as a harden failure.
    - Preserve behavior: keep the same returned payload shape and the same error message strings (e.g. authorizers must still fail with `"Unauthorized"` when expected).
    - Quick self-check: `rg -n "\\bcallback\\b|context\\.succeed\\b|context\\.fail\\b" -S .`
  - **Client retry overrides must be stripped**: keep existing behavior and do NOT set `maxAttempts` / `retryMode` when creating AWS SDK clients in code (unless explicitly requested):
    - `new DynamoDBClient({ ... })` → remove `maxAttempts` / `retryMode`
    - `new LambdaClient({ ... })` → remove `maxAttempts` / `retryMode`
  - **Handled errors policy must be present when applicable**: if the harden prompt/run mentions `handled-errors-policy` (or the lambda uses `CustomError`), ensure the repo includes the policy wiring and do not rely on harden flows to add it later:
    - A `custom_errors.policy.json` (v1) in the lambda root and an implementation module (commonly `handled_errors.js`) that reads it.
    - Policy schema requirement: `defaults` must include both `emit_requestid_success` and `log_event` (safe defaults: both `false`).
    - Add/merge string-literal `CustomError` codes into the policy under `errors.<code>` and keep both toggles policy-driven:
      - `emit_requestid_success`: controls `RequestId SUCCESS` emission for that code.
      - `log_event`: controls whether the redacted incoming event is logged for that code.
    - Add explicit entries for known handled codes (do not rely only on defaults). For auth flows, include `Unauthorized` explicitly so event logging can be controlled independently for JWT-verify failures.
    - For every lambda execution completion path (all terminal branches: early return, success return, handled error return, catch/failure return, and any other final outcome), always add distinct policy-controlled keys in `custom_errors.policy.json` (prefer `flags.*`) so each terminal path can independently control `RequestId SUCCESS` emission.
    - Event logging must remain policy-driven by `log_event`; when enabled, log the incoming event once (redacted, keep `event.body` intact).
    - Quick self-check: `rg -n "custom_errors\\.policy\\.json|handled_errors\\.js" -S .`
  - **Harden skill composition (mandatory):** when the active run uses `crp-repos-harden-pr` or `crp-repos-harden-deploy`, apply the embedded `ACTION:SLACK_COMMENT` error-context workflow in the same harden flow (combined execution).
    - During those harden runs, perform full-lambda handled-error coverage (entire lambda, not partial): inspect all terminal paths and all handled `CustomError` branches and synchronize `custom_errors.policy.json` accordingly.
    - In those harden runs, `custom_errors.policy.json` must contain explicit per-entry booleans for `log_event` (`true` or `false`) across policy-controlled entries (`errors.<code>` and `flags.<path_or_outcome>`); do not leave per-entry logging behavior implicit.
    - In those harden runs, keep `emit_requestid_success` policy-controlled per terminal outcome as already required.
    - In those harden runs, always stamp `package.json` `version` to show the latest harden timestamp. Keep the SemVer core (`X.Y.Z`) unchanged and set/replace build metadata to `+harden.YYYYMMDDHHmm` (Europe/Athens), e.g. `1.4.2+harden.20260218.1540`.
    - In those harden-pr runs, update/create top-level `package.json.harden_pr_timestamp` as a string with format `YYYYMMDDHHmm` (Europe/Athens), e.g. `202602181540`.
    - In those harden-deploy runs, update/create top-level `package.json.harden_deploy_timestamp` as a string with format `YYYYMMDDHHmm` (Europe/Athens), e.g. `202602181540`.
    - Update only the timestamp key that corresponds to the active harden flow (`harden_pr_timestamp` for harden-pr, `harden_deploy_timestamp` for harden-deploy`) and never delete the other key when present.
    - Keep the Slack action marker implementation (`ACTION:SLACK_HANDLED_ERROR_HE1=...`) and encoding rules under that combined harden flow.
    - Outside those harden skills, do not add or modify Slack action marker behavior unless the user explicitly requests it.

### Lambdas (AWS serverless)

- Path: `/home/dm-soft-1/Downloads/lambdas`
- Use this as the canonical source for:
  - Lambda names, handlers, event shapes, IAM policies, env vars
  - Shared libs/utilities used across lambdas
  - Cross-lambda references (SNS/SQS/EventBridge topics, DynamoDB tables, API Gateway routes, etc.)

### Application projects (frontends/backends/tools)

- Path: `/home/dm-soft-1/Downloads/projects`
- Use this as the canonical source for:
  - API clients, environment configuration, auth flows
  - UI flows and screens related to deliveries/couriers/devices
  - End-to-end flow behavior and integration points

### Required scanning approach

Before making claims about behavior, search the codebase.

- Prefer `rg` (ripgrep) for fast code search, e.g.:
  - `rg "delivery guy|courier|driver|device" /home/dm-soft-1/Downloads/lambdas`
  - `rg "login|auth|token|refresh" /home/dm-soft-1/Downloads/projects`
  - (Cross-repo trace)
    `rg "EventBridge|SNS|SQS|topic|queue|DynamoDB|authorizer|/deliveries" /home/dm-soft-1/Downloads/lambdas /home/dm-soft-1/Downloads/projects`

- Use `find` to enumerate lambdas/projects when needed:
  - `find /home/dm-soft-1/Downloads/lambdas -maxdepth 3 -type f -name "README.md" -o -name "package.json" -o -name "template.y*ml" -o -name "serverless.y*ml"`
  - `find /home/dm-soft-1/Downloads/projects -maxdepth 3 -type f -name "README.md" -o -name "angular.json" -o -name "package.json" -o -name "project.json"`

- Frontend→lambda mappings: treat `.codex/refs/codeliver-*-lambdas.md` as the source of truth. When a lambda is mentioned and we need to determine if it is called by a frontend, first check those refs; if confirmation is still needed, limit searches to `*.service.ts`; expand to other files only if explicitly requested by the user.

## 2.1 Cross-component debugging & bug-fixing (MANDATORY mindset)

When the user reports a symptom or asks to fix a bug, assume the issue may span multiple components. You should proactively trace across BOTH roots.

Minimum expectations when debugging:

- Identify the most likely entry point(s): API route, lambda handler, UI action, queue consumer, scheduled job, etc.
- Search for the integration edges:
  - API Gateway route strings, client base URLs, resource names, env var keys
  - Event names/detail-types, topic/queue names, table/index names, PK/SK patterns
  - Auth claims/roles/scopes and authorizer configuration
- Validate assumptions by reading code/templates:
  - Do not guess table names, topic names, env vars, IAM permissions—confirm from code or IaC.
  - If DynamoDB keys/indexes are involved, consult and maintain:
    - `.codex/playbooks/codeliver-dynamodb-keys-and-indexes.md`
- Produce an actionable fix:
  - Minimal diff, consistent style
  - Include any required updates in both lambda and project if the contract changed (payloads, fields, endpoints, validation)

## 2.2 Component-to-lambda impact analysis (MANDATORY when a project component is mentioned)

When the user mentions **any component/page/screen/service/feature** in a project, you MUST automatically perform impact analysis across connected lambdas/resources and report a concise impact summary without the user needing to ask.

### 2.2.1 Required impact outputs (always include)

Provide, at minimum:

1. **Impacted lambdas/resources (direct + 1-hop)**
2. **Potential negative impact / what might break**
3. **Frontend-change impact on lambdas (when frontend is changed)**
4. **No integration map unless explicitly requested by the user**

### 2.2.1.1 Explicit override rule

- If the user explicitly asks for an integration map, provide it.
- Otherwise, default output MUST remain a concise impact summary.

### 2.2.2 Minimum required scan steps (do not skip)

These scan steps are mandatory for technical validation. Keep the output as impact summary by default (not an integration map), while preserving direct + 1-hop downstream analysis depth.

- Locate the component and its route usage:
  - `rg -n "MyComponentName|selector:|export class .*Component" /home/dm-soft-1/Downloads/projects`
  - `rg -n "path:.*MyComponentName|loadComponent|loadChildren|component:" /home/dm-soft-1/Downloads/projects`
- Identify service dependencies and API edges:
  - `rg -n "constructor\\(|inject\\(|HttpClient\\b|fetch\\(|axios\\b" /home/dm-soft-1/Downloads/projects`
  - `rg -n "api|endpoint|baseUrl|environment\\.|/v1/|/api/" /home/dm-soft-1/Downloads/projects`
- Map each endpoint/event to lambdas by scanning IaC and handlers:
  - `rg -n "httpApi|httpApiEvent|events:|path:|method:|handler:" /home/dm-soft-1/Downloads/lambdas`
  - `rg -n "/your/route/here|detail-type|EventBridge|SNS|SQS|Topic|Queue" /home/dm-soft-1/Downloads/lambdas`
- Expand one hop downstream from each identified lambda:
  - Find publishes: `rg -n "publish\\(|SendMessageCommand|PutEventsCommand|EventBridge|SNS|SQS" /home/dm-soft-1/Downloads/lambdas`
  - Find data stores: `rg -n "DynamoDB|DocumentClient|PutCommand|UpdateCommand|QueryCommand|ScanCommand|S3" /home/dm-soft-1/Downloads/lambdas`
  - Then search who consumes those same resources (topics/queues/events/tables):
    - `rg -n "<topic-or-queue-or-event-or-table-name>" /home/dm-soft-1/Downloads/lambdas /home/dm-soft-1/Downloads/projects`

## 3) Mandatory documentation behavior (README + FAQ)

Any time you:

- explain a business flow, OR
- change a business flow, OR
- modify any lambda/project behavior,
  you MUST add or update a `README.md` in the relevant folder and ensure it ends with a section:

## “Συχνές ερωτήσεις (FAQ)”

### 3.0 README scope rule (KEEP IT SHORT)

- README files must describe the history.
- Do **NOT** include:
  - **“How to verify” sections**
- Keep updates minimal: only what an engineer/ops person needs to use, operate, and troubleshoot the component.

### 3.1 Which README must be updated/created?

- If the change is within a lambda folder: update/create `README.md` in that lambda’s root folder.
- If the change is within a project (frontend/backend/tool): update/create `README.md` in that project root folder.
- If the change spans multiple lambdas/projects:
  - Update each impacted component README (minimum), and
  - Optionally add a short “Integration Notes” section in the most central README.

### 3.2 README content requirements (minimum structure)

The README MUST include (in this order, unless a repo convention dictates otherwise):

1. **Overview**
   - What the lambda/project does and why it exists.
2. **Business flow**
   - Describe the flow in plain terms (create/update/delete delivery guy, device assignment, login, etc.)
   - Mention key invariants (e.g., unique identifiers, required states).
3. **Inputs & outputs**
   - For lambdas: include sample event JSON and sample response JSON.
   - For APIs: include sample request/response payloads.
4. **Configuration**
   - Required env vars (name, meaning, example).
   - Required AWS resources (tables, buckets, topics, queues) as discovered from code.
   - IAM requirements (high-level permissions, validated from code/templates).
5. **Examples**
   - Include at least:
     - One realistic “happy-path” example
     - One failure example with the expected error shape/message
     - (If relevant) one edge-case example
6. **Συχνές ερωτήσεις (FAQ)** (MANDATORY, at the very end)

### 3.3 FAQ requirements (ops-focused, no change tracking)

The FAQ section MUST explicitly cover:

- **Συνηθισμένες αποτυχίες / failure cases**
  - Typical errors, causes, and how to fix/diagnose
- **Επιπτώσεις σε σχετικές διαδικασίες**
  Must mention impact on:
  - login/auth
  - notifications (push/SNS/etc.)
  - dispatch/routes
  - cleanup (deletions, deprovisioning, orphan records)
- **Πώς επηρεάζονται άλλα components**
  - Which other lambdas/projects are likely affected and why (validated from code searches)
- **Παραδείγματα**
  - At least one Q/A with real payload/event snippets

The FAQ should be written in Greek (since it is user-facing/ops-facing), unless the repository convention requires English.

### 3.4 FAQ template (copy/paste)

Append something like this at the end of the README:

## Συχνές ερωτήσεις (FAQ)

### Γιατί αποτυγχάνει το login/auth;

- Πιθανές αιτίες:
  - (π.χ. missing env var, invalid token audience/issuer, authorizer mismatch, scope/role mismatch)
- Έλεγχοι:
  - (π.χ. logs, decoded JWT claims, env vars, API gateway authorizer config)

### Δεν έρχονται notifications. Τι να ελέγξω;

- (π.χ. SNS topic/event publish, device token mapping, permissions, dead-letter queues)

### Το dispatch/routes δεν ενημερώνεται σωστά. Τι να ελέγξω;

- (π.χ. EventBridge rules, SQS consumers, route recalculation triggers, ordering/idempotency)

### Έγινε delete/cleanup και έμειναν “ορφανά” δεδομένα. Τι κάνουμε;

- (π.χ. ποια tables/queues επηρεάζονται, πώς γίνεται re-run cleanup, remediation steps)

### Πώς επηρεάζονται άλλα components;

- (π.χ. ποια lambdas/projects καταναλώνουν/παράγουν αυτά τα events ή χρησιμοποιούν τα ίδια tables)

### Παραδείγματα

**Happy path**

```json
{
  "example": "..."
}
```

**Failure example**

```
{
  "error": "..."
}
```

Roadmap maintenance (MANDATORY)

A roadmap is a forward-looking artifact. For CodeDeliver, ROADMAP.md must be scannable and must answer three questions:

1. What is already delivered?
2. What is currently underway (or clearly unfinished)?
3. What should we do next?

Exception (ONE-TIME bootstrap per component):
When a ROADMAP.md is being created for the first time for a given lambda/project, it MUST be bootstrapped from the functional git commit history for that component scope (see 4.4). This establishes an accurate baseline of what shipped, while still keeping the roadmap readable (no per-commit history dump).

4.1 Placement rules (STRICT)

Lambdas:

- ROADMAP.md lives inside each lambda’s root folder (one per lambda).

Projects:

- ROADMAP.md is SINGLE per project and lives at the project root (next to that project’s package.json / angular.json / project.json).

Rules:

- Do NOT create ROADMAP.md files inside project subfolders (components/pages/features/services/modules).
- If multiple areas/components inside the same project are affected, capture everything in the single project-root ROADMAP.md.

  4.2 When to update ROADMAP.md

Whenever you propose changes that would reasonably be committed (feature, bug fix, refactor, contract change, config change), you MUST also update the relevant ROADMAP.md file(s) as part of the output.

4.3 ROADMAP.md structure (STRICT)

ROADMAP.md MUST contain exactly three top-level sections, in this exact order:

1. Completed
2. In Progress
3. Next

Rules:

- Do NOT add additional top-level sections.
- Do NOT include verification steps, command snippets, or changelog/history narration.
- Do NOT include commit-level metadata (messages/authors/dates/SHAs) anywhere in ROADMAP.md.

  4.4 FIRST-TIME creation of ROADMAP.md (ONE-TIME per lambda/project)

Goal:
Create a truthful baseline where:

- “Completed” is a milestone-style summary synthesized from all FUNCTIONAL commits affecting the scope path,
- without listing commits, authors, dates, SHAs, diffs, or file paths.

Hard rules:

- When a commit is classified as NON_FUNCTIONAL_ONLY, DO NOT include it in ROADMAP.md at all.
- For every included commit (FUNCTIONAL), you MUST read `git show <SHA> -- <SCOPE_PATH>` to understand the behavior change.
- ROADMAP.md MUST NOT include:
  - commit messages, SHAs, dates, or authors
  - per-commit breakdowns or “what changed in commit X” narratives
  - file names/paths or file-by-file change lists
- “Completed” MUST reflect the net/current behavior of the component (do not include features that were later removed/reverted).

  4.4.1 Define “NON_FUNCTIONAL_ONLY” commits (for filtering)

A commit is considered NON_FUNCTIONAL_ONLY for this roadmap scope if, within the scope path being documented, it ONLY changes files from the following allowlist:

- ROADMAP.md
- README.md
- outfile.json
- payload.json
- package.json
- package-lock.json

Notes:

- Apply this filter ONLY to files changed within the scoped path of the roadmap (lambda root folder or project root folder).
- If a commit changes any other file(s) in the scope path, it is FUNCTIONAL and MUST be treated as input to the “Completed” milestone synthesis.

  4.4.2 REQUIRED git-based workflow to build the baseline

Identify the git root:

- `git rev-parse --show-toplevel`

Choose the scope path for this roadmap:

- For a lambda roadmap: the lambda folder path (where ROADMAP.md will live)
- For a project roadmap: the project root path (where ROADMAP.md will live)

List commits affecting the scope path (oldest → newest):

- `git log --reverse --date=short --format="%H|%ad|%an|%ae|%s" -- <SCOPE_PATH>`

For each commit SHA in that list:

1. List files changed within the scope path:
   - `git show --name-only --pretty=format: <SHA> -- <SCOPE_PATH>`
2. Classify:
   - If and only if the changed files within scope are exclusively in the NON_FUNCTIONAL_ONLY allowlist → skip completely.
   - Otherwise → FUNCTIONAL.
3. For every FUNCTIONAL commit, read the diff within scope:
   - `git show <SHA> -- <SCOPE_PATH>`
4. Extract the behavior/outcome changes and synthesize them into milestone-style “Completed” bullets (see 4.4.3).

If git history is not available in the environment:

- Explicitly state that limitation and provide the exact commands the user should run locally.
- Ask the user to paste:
  - the `git log ... -- <SCOPE_PATH>` output, and
  - the `git show <SHA> -- <SCOPE_PATH>` diffs for the top N FUNCTIONAL commits at a time.

    4.4.3 How to write the three sections (content rules)

## Completed

- Write as milestone-style outcomes/capabilities that exist now (net/current behavior).
- NO commit metadata, NO per-commit narration, NO file/path mentions.
- Prefer business/feature language (“Supports X”, “Validates Y”, “Publishes event Z”) rather than implementation language.
- Keep it reasonably compact:
  - Aim for ~5–20 bullets depending on scope size.
  - Merge related commits into a single milestone where appropriate.

## In Progress

- Items that appear partially implemented, clearly unfinished, or started but not completed.
- Must be grounded in the current codebase state (not only commit history):
  - TODO/FIXME markers
  - stubs / “not implemented” branches
  - commented-out WIP blocks
  - obvious missing error handling/edge cases implied by current logic
  - failing or incomplete tests (if present)
  - missing config wiring implied by code
- Prefer checkboxes:
  - `- [ ] ...`
- If nothing is clearly in progress, include a single explicit line:
  - `- [ ] No in-progress items identified in the current codebase.`

## Next

- Concrete, component-specific follow-ups and improvement ideas (brainstorm), based on gaps/opportunities you observed while reading diffs and current code.
- Prefer higher-leverage items (reliability, ops, correctness, observability, contract clarity, idempotency).
- Prefer checkboxes:
  - `- [ ] ...`

# Roadmap

## Completed

- (Add milestone-style bullets that summarize the net/current delivered capabilities for this component.)

## In Progress

- [ ] (Add unfinished or partially implemented work items detected in the current codebase.)

## Next

- [ ] (Add concrete, component-specific follow-ups and improvement ideas.)

  4.5 Ongoing ROADMAP.md updates (after the first-time bootstrap)

After ROADMAP.md exists for a given lambda/project:

- Do NOT regenerate from git history unless explicitly requested.
- Keep the file forward-looking and current:
  - Move items from Next → In Progress when work starts.
  - Move items from In Progress → Completed when the work is actually shipped and present in the codebase.
- Keep “Completed” as a concise, net/current capability summary (avoid turning it into a per-release or per-commit history).

  4.6 Roadmap formatting rules (keep scannable)

- Use exactly the three required top-level headings in the required order.
- Completed:
  - Prefer plain bullets (no checkboxes) unless there’s a strong reason to use checkboxes.
- In Progress / Next:
  - Prefer checkbox lists (`- [ ]`).
- Avoid long narrative paragraphs.
- Do NOT add “How to verify” steps in ROADMAP.md (verification belongs in the assistant reply).

# Codex Workflow Guide (Policy + Skill Routing)

This file is the optimized operating policy for Codex sessions.

- Keep this file short and enforceable.
- Use skills for detailed execution playbooks.
- Full historical detail is preserved in `docs/AGENTS_FULL_REFERENCE.md`.

## 1) Start: confirm context

Always confirm:

- current repository/folder
- scope: `frontend`, `backend`, or `end-to-end`
- environments involved (`dev`/`stage`/`prod`) when relevant

## 2) Non-negotiable rules

### ClickUp task and write safety

- Ask for existing ClickUp task link/ID before ClickUp write operations.
- If no task exists, create one only after user confirms target List.
- Write only on tasks assigned to the requesting user.
- Treat tasks assigned to others as read-only.
- Do not change due date, priority, assignees, or move to done/closed unless explicitly requested.

### Mentions and language

- In ClickUp comments/descriptions/docs, use `@Display Name` mentions when notification intent exists.
- Chat with user in English by default.
- Mirror existing task language for ClickUp comments/descriptions.
- Write repo markdown docs in English.

### Approval and release controls

- Do not implement before explicit user go-ahead.
- Before any code changes, ask delivery mode and branch:
- `local changes only` or `PR-ready changes`
- target branch name (create/switch branch only after user confirms)
- Do not push or deploy without explicit user confirmation.
- Ask user: `push only` vs `deploy` before release actions.

### Time tracking and closure safety

- Manual tracking policy applies (record discussion start/end in Europe/Athens, add elapsed entry when work completes).
- When discussion on an existing task starts, move it to the list-specific `in progress` status (if available) at that time.
- Do not move task to done/complete/closed without a corresponding time entry.
- Move completed implementation tasks to testing-equivalent status (often `ΕΛΕΓΧΟΣ` / `ελεγχος`, list-dependent).
- Before any status change, explicitly discover statuses for the task's List (do not assume from other Lists).
- If the List has `in progress` and testing-equivalent statuses, use them (do not jump directly to `complete`).
- If a List truly has only terminal flow (for example `to do` + `complete`), ask explicit user confirmation before setting `complete`, and note this limitation in a task comment.

## 3) Skill routing (primary execution path)

Use these skills as the default source of detailed instructions.

1. `clickup-task-lifecycle`
- Task discovery, ownership checks, safe updates, status and time-entry rules.

2. `clickup-repo-linking`
- Repo-registry lookup/create and task-to-repo linking.
- Repo registry list: `901502503337`.
- Registry URL: `https://app.clickup.com/9015329079/v/l/6-901502503337-1?pr=90151074892`.

3. `implementation-gate`
- Architecture scouting, plan writing, ambiguity cleanup, approval gate, release gating.

4. `front-end-code-style`
- Angular Ionic frontend style for `mobileorder`/`dmpanel`:
- declaration order (`@Input/@Output` -> `public` -> `private`)
- camelCase naming
- NgRx subscription lifecycle patterns
- avoid non-trivial function calls in template bindings (precompute in `.ts`)

5. `back-end-lambda-code-style`
- Node.js lambda backend style for `dm_lambda_functions/paneldelivery`:
- keep deliveryManager helper usage and existing AWS SDK style per lambda
- prefer lodash + Bluebird iteration (`Promise.map`/`Promise.mapSeries`) over new loop constructs
- preserve DynamoDB params-object, `CustomError`, and response conventions

6. `closeout-docs`
- Testing status transition, closeout comments, final summaries, optional ClickUp docs.

7. `sync-global-codex-assets`
- Merge this repo's workflow overlay into `~/.codex/AGENTS.md` and sync the repo skills into `~/.codex/skills` with backup and a short sync report.

## 4) Standard workflow (condensed)

1. Confirm context and task scope.
2. Validate ClickUp task existence and ownership.
3. Ensure repo linkage is present before implementation.
4. Scout architecture and source-of-truth paths.
5. Write concrete implementation plan into ClickUp task description.
6. At discussion start: set list-specific in-progress status (if available) and start manual timing timeline.
7. Ask clarifying questions and request explicit go-ahead.
8. Ask delivery mode (`local changes` vs `PR-ready`) and target branch before editing files.
9. Implement minimal scoped changes, mirroring existing code style.
10. Run targeted validation (tests/build/lint as practical).
11. Ask `push only` vs `deploy`, then execute only what user confirms.
12. Move task to testing-equivalent status (if available), add change summary comment, and log time entry.
13. Provide concise final summary to user.

## 5) ClickUp MCP quick fallback

If ClickUp MCP fails because of auth/setup:

1. `codex mcp list`
2. If missing: `codex mcp add clickup --url https://mcp.clickup.com/mcp`
3. `codex mcp login clickup`
4. Verify with `codex mcp list --json`
5. Retry with narrower search scope

## 6) Optional documentation closeout

After implementation and validation, ask if user wants a ClickUp Doc:

- non-technical how-to
- technical/development handoff

When creating a ClickUp Doc, include/share with:

- `@Seirino`
- `@Constantinos Adamidis`
- `@Alexandros Nikolaos Naziris`

## 7) Full reference

For complete legacy workflow details, templates, and expanded procedures:

- `docs/AGENTS_FULL_REFERENCE.md`
