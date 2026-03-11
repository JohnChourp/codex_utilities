---
name: front-end-code-style
description: Apply the standard Angular Ionic frontend style for implementation and refactoring.
---

# Front End Code Style

Apply this style baseline before and during frontend edits.

## 1) App and stack context

1. Treat `mobileorder` and `dmpanel` as Angular + Ionic apps.
2. Follow existing Angular/Ionic and NgRx patterns from nearby components.
3. Keep quote style, formatting, and file structure aligned with touched files.

## 2) Variable declaration order and naming

Use this class member order in components/pages:
1. `@Input` / `@Output` decorators first.
2. `public` fields next.
3. `private` fields after public.
4. Constructor and methods after fields.

Naming rules:
1. Use `camelCase` for variables, fields, and methods.
2. Keep API payload keys unchanged when backend contracts require snake_case.
3. Use clear UI state names (`selectedStoreId`, `loginLoading`, `activeCoupons`).
4. Prefer typed models/interfaces for object variables when feasible (do not force large refactors just to add types).

## 3) Data and state handling style

1. Prefer lodash import/usage pattern already used in repo:
   - `import * as _ from "lodash";`
2. Prefer array/lodash transformations over `Map`/`Set` unless the same area already uses `Map`/`Set`.
3. Guard assignments from store/API with equality checks and deep copies:
   - `_.isEqual(...)` before assignment
   - `_.cloneDeep(...)` for stored local state

## 4) State management and subscriptions (NgRx)

Observed pattern in `mobileorder` components:
1. Subscribe with `this.store.select("slice")` (or selector functions).
2. Use RxJS operators like `distinctUntilChanged`, `auditTime`, `first` where needed.
3. Track long-lived subscriptions in `Subscription` fields or `Subscription[]`.
4. Create subscriptions in lifecycle hooks (`ngOnInit`, `ionViewDidEnter` when view-driven).
5. Always unsubscribe in teardown hooks (`ngOnDestroy`, `ionViewDidLeave`).

## 5) Template performance rule

1. Avoid calling non-trivial functions directly from template bindings (`*ngIf`, `*ngFor`, interpolation, `[prop]`) because they run during change detection.
2. Compute view variables in `.ts` (during state updates/lifecycle hooks) and bind plain values in `.html`.
3. Event handlers in templates are still valid (`(click)="openModal()"`, `(ionChange)="onChange($event)"`).
4. If legacy code already has template function calls, avoid adding new ones and migrate touched paths to precomputed variables.

## 6) Modal UI conventions (Ionic)

1. For modal dismiss actions, use an icon-only close button in the header (`ion-icon name="close"`), not a text `Close` button.
2. Keep modal close action in header-right (`ion-buttons slot="end"`), consistent with `dm-kds-app` and `pospanel` modal patterns.
3. Place primary save actions in `ion-footer` (inside `ion-toolbar`/button container), not in scrollable modal content.
4. Preserve save loading/disabled states when moving actions to footer.
5. Apply these rules to create/edit modals unless an existing touched flow explicitly requires a different UX.

## 7) Scope rules

1. Keep changes minimal and localized.
2. Preserve contract compatibility while improving style consistency.
3. Do not introduce new architectural patterns unless explicitly requested.
