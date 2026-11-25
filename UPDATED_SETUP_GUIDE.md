# Nexora AI E-Commerce – Windows / PowerShell setup

## 0. Before replacing your current folder

- Keep the existing project folder as a backup.
- Export/backup the MySQL database. Do not drop the database or delete product/user/recommendation records.
- The updated ZIP intentionally does not include the original `backend/.env`, virtual environment, `node_modules`, or runtime cache files. Keep your original `.env` privately, or create a new one from `backend/.env.example`.
- The uploaded archive contained a database password in `.env`. Rotate that MySQL password before using the project in production, and do not share `.env` files.

## 1. Backend

Open PowerShell in the extracted project:

```powershell
cd .\backend
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and set the MySQL database name, username, password, host, `DJANGO_SECRET_KEY`, allowed hosts and CORS origins. Make sure MySQL is running and the configured database already exists.

Back up the database, then run:

```powershell
python manage.py migrate --fake-initial
python manage.py check
python manage.py createsuperuser
python manage.py runserver
```

If an existing `orders_order` or `orders_orderitem` table has a different structure from the original models in the supplied ZIP, stop before migration and inspect the schema. Do not use `flush`, `migrate zero`, or drop/recreate the database.

## 2. Frontend

Open a second PowerShell terminal:

```powershell
cd .\frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Set `VITE_API_URL=http://127.0.0.1:8000/api` in `frontend/.env` for local development if required. For a production frontend, set it to your deployed Django API URL and rebuild:

```powershell
npm run build
```

## 3. Configure merchant payments

1. Sign in with the Django admin/superuser account in the React application.
2. Open **Dashboard → Payment settings**.
3. Enter the store/merchant name and your official business UPI ID.
4. Upload the official merchant UPI QR image.
5. Enable UPI and COD, then save.
6. Place a test COD order.
7. Place a test UPI order only after the merchant QR is configured. Check the actual credit in the merchant bank/merchant dashboard before verifying a UTR.

UPI QR mode is manual collection and manual verification. It does not provide automatic bank callbacks or gateway settlement. Never ask a customer to share their UPI PIN or OTP.

## 4. Product uploads

Admin or approved sellers can add products using either an image URL or the **Add from Media** file picker. Product specifications are entered one per line, for example:

```text
RAM: 16 GB
Storage: 512 GB SSD
Display: 15.6-inch FHD
Processor: Intel Core i7
```

Uploaded files are stored in Django `MEDIA_ROOT`. Configure persistent media storage before deploying; many application hosts erase local uploaded files when instances are replaced.
