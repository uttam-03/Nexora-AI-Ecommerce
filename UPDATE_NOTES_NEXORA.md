# Nexora AI E-Commerce — update notes

## Implemented in this package
- Dashboard greeting based on time of day and account display name, plus Admin/Seller role badge.
- Profile editor for first/last name, email, phone, bio, address, city, state, postal code and avatar upload.
- Profile fields added to the Django custom user model and migration `0004_profile_fields.py`.
- Product images in product cards load lazily and decode asynchronously.
- Shop search can be submitted by Enter; loading/error states were added to the catalogue page.

## Setup
- Backend: create/activate your own Python environment, install `backend/requirements.txt`, copy `.env.example` to `.env`, configure database/keys, then run `python manage.py migrate` and `python manage.py runserver`.
- Frontend: run `npm install`, configure `frontend/.env` from `.env.example`, then `npm run dev`.
- Production: configure secrets and host/origin settings in your hosting provider; do not commit `.env` files.

## Verification limitation
The frontend build could not be fully verified in this packaging environment because the bundled optional Rollup Linux native dependency was absent. The backend was syntax-compiled, but Django runtime checks/migrations were not executed here because Django is not installed in the active environment. Please run the setup commands and test in your own environment before production deployment.
