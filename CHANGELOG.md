# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-23

### Added
- Initial release
- `trending()` - Realtime trending keywords via RSS (fast, ~20 items)
- `trending_bulk()` - Bulk trending data via Selenium (~100 items)
  - CSV/JSON export with `output` parameter
  - Enriched export with `enrich=True` (news, images, related queries, metadata)
- `related()` - Related search queries for a keyword
- `compare()` - Compare keywords by average interest
- `interest()` - Interest over time with platform support (web, youtube, images, news)
- CLI commands: `trend`, `bulk`, `rel`, `cmp`, `hist`
- MCP server with 4 tools: `trends_trending`, `trends_related`, `trends_compare`, `trends_interest`
- Token-optimized output formats: minimal, standard, full
