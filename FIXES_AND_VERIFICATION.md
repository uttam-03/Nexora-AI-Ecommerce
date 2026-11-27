# Nexora AI E-Commerce — Fixes & verification status

## Changes applied in this package
- Production Django `DEBUG` now defaults to false and requires a configured secret key when not in debug mode.
- Added production HTTPS-related security settings (secure cookies, HSTS, content-type protection, frame denial) when `DEBUG=False`.
- Address and payment-method default selection no longer mutates database state during serializer validation; default-selection writes happen transactionally during save.
- Product serializer rejects a discount price greater than or equal to the regular price and writes specifications transactionally.
- UTR submission now locks the order within a transaction to reduce concurrent duplicate-state updates.
- Product card images use lazy loading and async decoding; shop search requests debounce input changes.
- Dashboard greeting, role/name display, profile editing and avatar upload are present in the frontend package.

## Verification performed
- Python `compileall` completed successfully for backend source.
- Frontend production build was not verified: dependency installation timed out and Vite/Rollup binaries were unavailable in this environment.
- Django runtime checks, database migrations, API integration tests, payment workflow tests, media persistence tests and production Render tests were not run.

## Deployment caution
Do not deploy directly to production without running the frontend build, Django checks, migrations against a backed-up database, and end-to-end smoke tests. UPI manual verification is not an automatic payment gateway. Durable production media storage and database-level UTR uniqueness remain deployment/database-specific work.
