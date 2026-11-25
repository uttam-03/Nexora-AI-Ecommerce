# Nexora AI E-Commerce — Admin & Seller Workspace

## Roles and account security
- Customer registration is public.
- Seller registration is public as an application; seller accounts start unapproved.
- Admin accounts cannot be registered from the website or created from the dashboard.
- Create the platform administrator only with Django's `createsuperuser` command. The custom user manager assigns role `ADMIN`; the migration also upgrades existing superusers to `ADMIN`.
- Admin can approve sellers, block/unblock accounts, and deactivate/remove seller or customer accounts. Deactivation preserves order history and audit records.
- A blocked seller is unapproved and their products are hidden from the public catalogue.

## Admin dashboard
- Live counts for customers, sellers, pending sellers, products, orders, complaints, reviews and order revenue.
- Add customer/seller accounts (never admins), approve sellers, block/unblock or deactivate accounts.
- Add/edit/delete products, view all orders, review public complaints and feedback, update complaint status and write an admin response.

## Seller dashboard
- Seller access requires admin approval.
- Add/edit/delete own products; sellers cannot edit another seller's products.
- View orders containing their products, customer product reviews and service feedback addressed to them.

## Customer feedback
- `/feedback` lets authenticated customers submit complaints, service issues, general feedback and product reviews.
- Product reviews are visible to the relevant seller. Admin can moderate through Django Admin.

## Setup
Backend (PowerShell):
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Configure MySQL credentials in backend/.env before running migrations.
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Frontend:
```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. Sign in with the superuser credentials and open `/dashboard` for the admin workspace. Sellers can sign up from the normal registration page; an admin must approve them in Admin Dashboard → Users & sellers.

## API endpoints
- `GET /api/dashboard/overview/`
- `GET /api/dashboard/orders/`
- `GET|POST|PATCH|DELETE /api/dashboard/admin/products/` (detail routes for item operations)
- `GET|POST|PATCH|DELETE /api/dashboard/seller/products/` (approved seller's own products)
- `GET /api/dashboard/admin/users/`, `POST /api/dashboard/admin/users/create/`, `PATCH|DELETE /api/dashboard/admin/users/<id>/`
- `GET|PATCH /api/dashboard/admin/feedback/` (admin)
- `GET /api/dashboard/seller/feedback/`, `GET /api/dashboard/seller/reviews/`
- `POST /api/dashboard/feedback/`, `GET|POST /api/dashboard/reviews/`

The project uses the configured MySQL database. Back up the database before applying migrations to an existing deployment. No production data is deleted by these migrations.
