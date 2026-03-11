# CodeDeliver Cross-Project Parity Rules (On-Demand)

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

