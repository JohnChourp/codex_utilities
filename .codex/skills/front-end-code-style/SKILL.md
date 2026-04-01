---
name: front-end-code-style
description: Apply the standard Angular Ionic frontend style for implementation and refactoring.
---

# Front End Code Style

Apply this style baseline before and during frontend edits.

## 1) App and stack context

1. Treat `mobileorder`, `dmpanel`, `codeliver-sap`, `codeliver-panel`, `codeliver-pos`, `codeliver-app`, and `cloud-repos-panel` as supported Angular + Ionic apps for this baseline.
2. Use `mobileorder` and `dmpanel` as canonical style references, but apply the same frontend baseline across the supported Angular/Ionic repos above.
3. When work happens from the shared `~/Downloads/projects` workspace, apply this baseline to touched Angular/Ionic frontend repos within that workspace rather than treating it as repo-specific guidance.
4. Follow existing Angular/Ionic and NgRx patterns from nearby components.
5. Keep quote style, formatting, and file structure aligned with touched files.

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

Observed shared pattern across supported Angular/Ionic repos:

1. Subscribe with `this.store.select("slice")` (or selector functions).
2. Use RxJS operators like `distinctUntilChanged`, `auditTime`, `first` where needed.
3. Track long-lived subscriptions in `Subscription` fields or `Subscription[]`.
4. Create subscriptions in lifecycle hooks (`ngOnInit`, `ionViewDidEnter` when view-driven).
5. Always unsubscribe in teardown hooks (`ngOnDestroy`, `ionViewDidLeave`).

## 5) Template performance rule

1. For Angular 20+ repos, use built-in control flow blocks (`@if`, `@for`, `@switch`) and do not add new `*ngIf`, `*ngFor`, or `*ngSwitch` usages. Non-Angular structural directives such as `*transloco` are exempt.
2. Avoid calling non-trivial functions directly from template bindings (`@if`, `@for`, interpolation, `[prop]`) because they run during change detection.
3. Compute view variables in `.ts` (during state updates/lifecycle hooks) and bind plain values in `.html`.
4. Event handlers in templates are still valid (`(click)="openModal()"`, `(ionChange)="onChange($event)"`).
5. If legacy code already has template function calls, avoid adding new ones and migrate touched paths to precomputed variables.

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
