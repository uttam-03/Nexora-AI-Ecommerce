# Nexora AI E-Commerce – implementation update

This update keeps the existing React + Vite frontend, Django REST Framework backend, MySQL configuration, accounts, catalogue, cart, recommendations, chatbot and dashboard modules.

## Implemented in this update

- Product cards open a product detail route (`/product/<slug>`).
- Product detail page shows description, stock, price, quantity controls, Add to Cart, Buy Now and saved product specifications.
- Cart page loads the authenticated user's cart, updates quantities, removes items and shows subtotal.
- Checkout supports saved/new delivery addresses and UPI QR or COD.
- UPI order creation is blocked until an admin configures both a merchant UPI ID and QR image.
- Customer can submit a UTR; it remains pending until an admin checks the merchant bank credit and verifies it.
- COD remains pending until delivery; admin can mark collection after the order is delivered.
- Admin dashboard includes UPI/COD settings and a payment verification panel.
- Product forms accept an image URL or an image file upload, plus one specification per line (`RAM: 16 GB`).
- Customer order/payment history and a print/save-as-PDF order receipt are available.
- Cart and checkout validate quantities and stock on the server.
- Admin cancellation restores reserved stock for unpaid orders. Paid orders require a refund process before cancellation.

## Important setup steps

1. Back up the MySQL database before applying migrations.
2. Create `backend/.env` from `backend/.env.example` and enter your own DB credentials and Django secret key. Never commit or share `.env`.
3. Install backend dependencies from `backend/requirements.txt`.
4. From `backend/`, run `python manage.py migrate --fake-initial`.
   - The `orders` app previously had no migration files in the supplied ZIP. Its first migration reflects the original Order/OrderItem schema; `--fake-initial` allows Django to adopt those tables if they already exist.
   - Review migration output. If an existing table has a schema different from the supplied original models, stop and take a schema backup before proceeding.
5. Run `python manage.py createsuperuser` if an admin account does not already exist.
6. Start Django with `python manage.py runserver`.
7. From `frontend/`, run `npm install`, set `VITE_API_URL` in `.env` if needed, and run `npm run dev`.
8. Log in as admin, open Dashboard → Payment settings, enter the merchant UPI ID, upload the official merchant QR image, and enable UPI/COD as required.
9. Test COD and UPI using a low-value test order. For UPI, check the actual bank/merchant account credit before pressing Verify. A UTR or screenshot alone is not proof of payment.

## Media and production deployment

Uploaded product and QR images are stored under Django `MEDIA_ROOT`. Local development serves these through Django's media URL configuration. On production, configure durable media storage (a persistent disk or object storage) and HTTPS; do not rely on an ephemeral deployment filesystem for customer/product uploads.

## Verification notes

- Python source files passed `compileall` syntax validation.
- React JSX files passed Babel parser validation.
- A full Vite production build could not be run in the build container because the supplied `node_modules` did not contain Rollup's Linux optional binary and network access was unavailable. On the target machine, run `npm install` followed by `npm run build`.
- Django runtime checks and database migrations were not executed in this container because Django dependencies were not installed and package network access was unavailable. Apply migrations only after backing up the actual database.

## Payment lifecycle

- UPI: `PENDING` → customer submits UTR → `SUBMITTED` → admin bank-credit verification → `PAID` / `CONFIRMED`.
- COD: `PENDING` → order delivered → admin records collection → `PAID`.
- Rejected UPI references can be resubmitted. Duplicate UTR values across different orders are rejected.
- This is manual UPI QR collection, not an automatic bank/payment-gateway callback integration.
