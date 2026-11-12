# Changelog

## [In Development] - Unreleased

<!--
> [!NOTE]
>

> [!TIP]
>

> [!IMPORTANT]
>

> [!WARNING]
>

> [!CAUTION]
>

Section Order:

### Added
### Fixed
### Changed
### Removed
-->

<!-- Your changes go here -->

### Added

- Optional extra `tests-allianceauth-development` (test packages plus the Alliance Auth 6 pre-release) and test settings in `testauth/settings/development/` for the tox environment `allianceauth-development` and `make tox-tests-development`; a non-blocking CI job "AA Development" runs it on Python 3.13 and 3.14

### Changed

- [CHANGE] Added a test that compares every permission string used in the code (`corptools_doctrine.<codename>`) with `General.Meta.permissions`, so a wrong app label or codename is found by the tests. The codenames and texts are unchanged
- [CHANGE] The `AppLogger` is created only once in `corptools_doctrine/providers.py`. `api/doctrine.py`, `api/manage.py` and `managers/doctrine_manager.py` import it with `from corptools_doctrine.providers import logger` instead of building their own; `api/helpers.py`, `decorators.py`, `models/doctrine.py`, `models/general.py` and `views.py` created a logger they never used, it is removed there. Log records now carry the logger name `corptools_doctrine.providers` instead of the module name; the prefix is unchanged.
- [CHANGE] Language files other than `en` hold only real translations as Weblate writes them (empty placeholders removed, `{}` while nothing is translated); `i18next-scanner` maintains only `en`, and missing keys fall back to English
- [CHANGE] `aa-geuthur-react` raised to `^1.3.0`. The package bundles its own translations and registers them with i18next through `AaReactProvider`, so `Main.tsx` lists only the namespace `translation`, the copies under `corptools_doctrine/static/corptools_doctrine/i18n/<lng>/aa-geuthur-react.json` are removed and `make react-copy-translations` no longer copies them. Untranslated strings in `frontend/i18n/<lng>/translation.json` are empty instead of English (`i18next-scanner` writes the key as value only for `en`); `returnEmptyString: false` shows the English fallback at runtime. The translation files now contain all texts of the frontend again (92 keys added since v1.0.0). Translate on Weblate as before.
- GitHub workflows, `dependabot.yml` and `testauth/settings/base.py` follow the template: `autotester.yml` has the `env:` block, uses the pinned Redis action and a separate React job (lint, tests, build) that the Python matrix waits for; the test settings use the `cleanup_token_subset` task, `DeviceDetectionMiddleware`, `STORAGES`, `DISPLAY_DEBUG` and the log levels of the template
- Python 3.10 is no longer supported: `requires-python` is now `>=3.11,<3.15`; the CI matrix and `tox.ini` cover Python 3.11 to 3.14, `tox.ini` passes `USE_MYSQL` through and no longer uses `usedevelop`
- The shared React base comes from the npm package [`aa-geuthur-react`](https://github.com/Geuthur/aa-geuthur-react) 1.2.0 (BaseTable stack, BaseModal, loaders, menu, `useMenu`, `useUserData`, `AuthBase`, `ErrorPage`, utils, `createApiClient`, `queryKeys`, styles, ESLint rule `import-headings`). `Routing.tsx` wraps the app in `AaReactProvider`, `Styles/index.css` imports `aa-geuthur-react/styles.css` first, `apiClient` is `createApiClient<paths>()` and the app query keys extend the `queryKeys` of the package
- The frontend follows the structure of the template: `App.tsx` is now `Routing.tsx`, `main.tsx` is `Main.tsx`, `configuration.ts` is `constants.ts`, `index.css` moved to `Styles/index.css`, and `react-router` is imported as `react-router-dom`
- The page layout is the `AuthBase` of the package (container 640 px to 1280 px, narrower screens use the full width); the `aa-section` wrapper is gone
- The tables use the `BaseTable` of the package: the `variant` prop is gone (the former `vowra` look is the default), the footer is the layout of the package, the matrix view keeps its sticky header and first column through classes of the app (`corptools-matrix`)
- The `menu/` endpoint can deliver `badge` and `has_errors` per link (both optional), as defined by the contract of the package
- Tests now create users, characters, corporations and alliances with the `aa-evesde-factory` factories and an own `UserMainFactory` instead of `create_user_from_evecharacter`, `load_allianceauth` and `allianceauth.json`; the unused test helpers were removed
- Test helpers (`add_character_to_user`, token helpers, `add_permission_to_user`) now come from `aa-evesde-factory` instead of own copies in `corptools_doctrine/tests/testdata/utils.py`
- Test base class `DoctrineCheckerTestCase` replaced by `AuthTestCase` (same structure as the other apps: `NoSocketsTestCase`, `AuthTestCase` with `factory`, `user` and `superuser`); the extra users, corporations and item types moved into the tests that use them
- Raise the ESI compatibility date from `2025-12-16` to `2026-08-18`
- Ship the ESI OpenAPI spec for compatibility date `2026-08-18` with the package, so the ESI client loads it from the file instead of downloading it at runtime

### Fixed

- ESI client raising `AttributeError` with `DEBUG=False` because of an empty operations filter; it now uses the public `GetStatus` operation
- Fixed `make coverage` exiting with 0 when tests failed. The reports are still created, and the target now exits with the status of the test run, or with the status of `coverage report` if the tests passed.

### Removed

- The copies of the shared modules and their tests: `Components/Base/{BaseTable,BaseModal,Loader,BaseHeader}`, `Menu/`, `Utils/{bootsTrap,eveOnline,general}`, `Pages/Base.tsx`, `Pages/404.tsx`, the CSS modules of the BaseTable, loaders and modals, `eslint-rules/`, the table, loader and `aa-section` rules of `Styles/index.css` that the package ships; `loadMenu` and `loadUserData` of `Api/ApiCalls.ts` (now in the package); the dev dependency `openapi-typescript-helpers`
- The "Showing x-y of n items" line of the table footer and the `itemLabel` prop (the table of the package has no such line)
- Outdated test settings `testauth/settings/aa5/`, replaced by `testauth/settings/development/`

## [1.0.0] - 2026-01-11

### Added

- React SPA frontend with modernized Alliance Auth BS5 template, TanStack Table, React Query, Lucide icons, and Bootstrap 5 styling
- Dedicated frontend pages: `DoctrinesPage`, `CorporationDoctrinesPage`, `OverviewPage`, and `ManagePage`
- Corporation Doctrines member overview with Badges View (featuring Ready/Not Ready badges and progress indicators) and Matrix View toggle with sticky header and frozen first column
- Progressive chunked background auditing on the frontend with live status spinners, individual row updates, and header audit progress bar
- Interactive modals: `MissingSkillsModal` with clipboard copy helper and `DoctrineSkillsModal` with trained vs. missing skill level indicators
- Composite database indexes on `Doctrine` (`category`, `skilllist`) for covering index execution

### Changed

- Significantly improved doctrine evaluation performance across personal and corporation audits:
  - Bulk-prefetched skills filtered to doctrine-required skills only, eliminating table scans and filesorts
  - Replaced multi-level loops in `SkillListHandler` with direct dictionary mappings
  - Added `DoctrineAuditFilter` (`ninja.FilterSchema`) for efficient query filtering in member audits
- Optimized personal Doctrines page (`DoctrinesPage`) with sectional, on-demand loading per character, local cache persistence, and instant character switching
- Converted tables in `DoctrineSkillsModal` and `MissingSkillsModal` into paginated, searchable `BaseTable` DataTables
- Replaced database & Redis caching (`DoctrineCache`) with optimized bulk database queries and direct indexing
- Modernized backend REST endpoints to typed Ninja schemas with automatic OpenAPI generation

### Fixed

- Fixed Corporation Doctrines skill evaluation bug where user objects were not normalized to integer IDs in bulk queries
- Fixed Corporation Doctrines page displaying logged-in user's corporation name instead of the target corporation name when navigating from Overview or direct URL

### Removed

- Removed legacy Django template views, server-side templates, jQuery scripts, and `DoctrineCache` model

- Removed unused user settings page, components, and endpoints

- Removed obsolete cache hashing helpers (`_build_account_cache_key`, `_get_chars_hash`, `_get_skill_list_hash`) and unused dead methods (`fittings_installed`, `_find_character_skills`, `MissingSkillsSchema`)

- Initial Release

[1.0.0]: https://github.com/Geuthur/aa-corptools-dc/compare/v...v1.0.0 "v1.0.0"
[in development]: https://github.com/Geuthur/aa-corptools-dc/compare/v1.0.0...HEAD "In Development"
