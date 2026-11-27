# Nexora AI — Responsive and catalogue upgrade notes

## Included in this update
- Product catalogue UI now shows a loading state, retry notice, and pagination controls when the API response uses paginated `results/count` format.
- Search submit resets catalogue paging to page 1.
- Responsive CSS polish for catalogue controls, product cards, dashboard layout, profile, cart/checkout, and narrow mobile screens.
- Profile/avatar editing and role/name greeting functionality already existed in the source project; retained rather than duplicating it.

## Important verification limitation
A production build could not be verified in this environment because the frontend's installed Rollup dependencies are incomplete (`@rollup/rollup-linux-x64-gnu` missing). Run `npm ci` in `frontend` in a clean local environment and then `npm run build`.

## Backend pagination caveat
The frontend expects a Django REST Framework paginated catalogue response (e.g. `{count, next, previous, results}`). If catalogue pagination is not configured in backend settings, the controls may not work correctly; verify the catalogue endpoint and configure a page size.

## Local check
1. Extract the archive.
2. In `frontend`, run `npm ci` and `npm run build`.
3. Run the backend and frontend as described in the project's setup guide.
4. Check desktop, tablet, and mobile widths; test login as admin, seller, and customer; test profile save and avatar upload.
