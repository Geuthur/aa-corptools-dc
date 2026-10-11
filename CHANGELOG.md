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
