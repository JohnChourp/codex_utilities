# CodeDeliver General Working Rules Policy (On-Demand)

Load this policy when a task needs non-MCP, non-ClickUp, non-lambda-hardening behavioral rules.

## General implementation and UX rules

- Prefer minimal, style-consistent changes; avoid large refactors unless explicitly requested.
- When changes are needed in files under `ios/` or `android/` (regenerated on deploy), do **not** edit those files directly. Create/update a script (e.g., `build-before.js`, `build-after.js`, `capacitor-project.ts`) that applies the changes during build/deploy.
- In repos that ship live JS updates, do **not** introduce a new native plugin path or native-only method call unless the already installed binaries contain it. If binary compatibility is uncertain, keep the JS path guarded and provide a fallback that works on the currently deployed app version.
- In non-Plan mode, ask clarifying questions for every non-trivial task, meaningful scope change, parity choice, or risky assumption before implementation. Only skip questions for clearly trivial single-step tasks with one safe interpretation.
- **Re-entrant pending-selection safety (mandatory):** when implementing any pending UI selection flow that opens map markers/info windows (or any handler that can trigger state refresh), always apply `clear-before-open` and `restore-on-miss`.
  - Required pattern: copy pending id locally -> set pending state to `null` -> attempt selection/open -> if selection target is missing, restore pending id.
  - Forbidden pattern: clearing pending id only after `open...()`/selection handler returns, because those handlers may synchronously trigger refresh cycles and re-enter the pending-flush method, causing recursion and stack overflows.
  - Quick self-check: verify no cycle of the form `flushPending* -> open/select* -> refresh* -> flushPending*` can run with the same pending id still set.
- **Plan Mode question UX (mandatory):** when in Plan Mode, ask clarifying questions through the interactive options UI (`request_user_input`) and avoid posting free-form question lists in plain chat. Keep asking through the interactive UI until required decisions are collected, then present the final plan so the user can choose “Implement Plan”.

## Frontend translation and template rules

- Translation rule (UI text in templates): never hardcode user-visible labels/messages/statuses (including Greek text such as `ενεργο` / `ανενεργο`) directly in templates. Always use the translate pipe with a key (e.g., `{{ "store-status-active" | translate }}`) and add/update that key in **every** `src/assets/i18n/*.json` language file.
- Translation completion gate (mandatory): for every change that adds/updates translation key usage (`| translate`, `translate.instant`, `translate.get`, `translate.stream`), run a key-coverage check against all `src/assets/i18n/*.json` files of the impacted frontend project before completing the task.
  - If any used key is missing from at least one locale file, the task is **not complete**.
  - Final reply must include: (a) the checked key set, and (b) the locale files where keys were added/updated.
- Broken translation audit (mandatory): after any frontend project change, scan for unresolved translate usage and raw key leaks such as `groups.informations`; if a key is missing or a dotted parent collides with a string key, fix the locale files or key structure in every impacted `src/assets/i18n/*.json` file before closeout.
- Translation key safety: do not introduce dotted translation keys that collide with existing **string** keys (e.g. avoid `statistics.week-grouping-hint` if `statistics` is already a string). Prefer flat keys like `statistics-week-grouping-hint`, or ensure the parent key is an object in all locales.
- UI affordance rule (chips): do **not** render `ion-chip` elements that look clickable but perform no action on tap/click. If the content is informational only, use `ion-badge`, `ion-text`, `ion-label`, or plain text containers instead.

## Engineering quality rules

- Logging: when dumping events for troubleshooting, do not redact `event.body`; keep it intact while still redacting auth tokens, cookies, and passwords.
- **Clarity over efficiency:** if there is a trade-off between performance and readability/maintainability, prefer the simplest correct implementation (even if it is less efficient).
- **TypeScript and ESLint gate (mandatory):** for every project or lambda change, run the narrowest relevant validation for the touched repo plus `npx eslint` on every changed lintable source file from the relevant root before closeout. Treat TypeScript compile errors, `used before initialization` / field-order issues, unresolved imports, `no-undef`, and other ESLint failures as blocking and fix them before proceeding.
- **Angular/Ionic build gate (mandatory):** for every Angular/Ionic project change under `projects/`, run `ionic build` for the touched repo after targeted validation. If the build fails, fix the reported TS/template/build errors and rerun `ionic build` until it passes. Do not close out while the build is red.
- **Class field initialization safety (mandatory):** never initialize a class field with a value that depends on another field declared later in the class. If a derived value needs another member, declare the dependency first or move the derivation into the constructor or a lazy getter.
- **Angular time-binding safety (mandatory):** never call `Date.now()`, `moment().fromNow()`, or any other current-time calculation from a template-bound method/getter/binding. This includes `[max]`/`[min]`, ETA badges, "ready in", and "x minutes ago" labels.
- **Angular time-binding pattern (mandatory):** when the UI depends on "now", keep a stable component field such as `nowMs` or a cached derived label, update it from a controlled timer/signal, and have template-bound helpers read only that stable state.
- **Angular repeated time-label rule (mandatory):** if the same relative-time/ETA label is rendered multiple times in one template, precompute/cache it in component state or a view-model instead of recalculating it from the template.
- Reference pattern: `projects/codeliver/codeliver-panel/src/app/shared/common/request-item/request-item.component.ts` and `projects/codeliver/codeliver-pos/src/app/shared/common/request-item/request-item.component.ts` keep a stable `dateNow` that template-bound helpers consume.
- Avoid `ng-template`/`ngTemplateOutlet`; keep the full markup inline inside each `@for` loop, even if it duplicates markup.
- **Angular 20+ control-flow rule (mandatory):** in Angular 20+ projects, use built-in control flow blocks (`@if`, `@for`, `@switch`) by default and do not introduce new `*ngIf`, `*ngFor`, `*ngSwitch`, `*ngSwitchCase`, or `*ngSwitchDefault`.
- Exception: non-Angular structural directives such as `*transloco` are allowed when the library API requires them.
- Ionic modal safety rule (componentProps vs signals): values passed through `modalController.create({ componentProps: ... })` are assigned directly on the component instance. Do **not** model those props as callable signal inputs (`input()` / `InputSignal`) unless callers pass signals explicitly. For primitive/array/object props (e.g. `mode`, `title`, `items`), use plain `@Input()` properties; otherwise runtime errors like `TypeError: this.<prop> is not a function` can occur.
- **Dependency hygiene (always):** remove unused dependencies from `package.json`; do not keep deps “just in case”.
