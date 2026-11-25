# Nexora AI Ecommerce — Render Deployment Guide

## Is ZIP mein kya fix hua
- `cart` app ki missing initial migration add ki gayi. Isse `Cart` aur `CartItem` tables migrate ho sakengi; existing products/users/orders ko delete ya reset nahi kiya jata.
- Gunicorn aur WhiteNoise dependencies add ki gayi; Django static files ke liye `collectstatic` support configure hai.
- Production settings: `DEBUG=False`, secret key validation, Render HTTPS proxy/cookie settings, CORS/CSRF environment variables aur optional MySQL SSL (`DB_SSL=true`).
- 250-tech-product additive seed command aur CSV dataset include hai. Ye existing catalogue ko delete nahi karta.

## 1) GitHub par project push
ZIP extract karke project root `Nexora_AI_Ecommerce` ko GitHub repository mein push karein. `.env` ya passwords commit mat karein.

## 2) MySQL database
Existing MySQL database hi use karein. Provider ke dashboard se database name, username, password, hostname aur port copy karein. Agar provider SSL/TLS require karta hai to `DB_SSL=true` rakhein. Database ko delete/recreate mat karein.

## 3) Render backend Web Service
- New → Web Service → apna GitHub repo select karein.
- Root Directory: `backend`
- Runtime: Python 3
- Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- Start Command: `python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

Environment variables add karein:
- `DEBUG` = `False`
- `DJANGO_SECRET_KEY` = long random secret (unique)
- `ALLOWED_HOSTS` = `your-backend-name.onrender.com`
- `CORS_ALLOWED_ORIGINS` = `https://your-frontend-name.onrender.com`
- `CSRF_TRUSTED_ORIGINS` = `https://your-frontend-name.onrender.com`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` = MySQL provider ke exact values
- `DB_SSL` = `true` if provider requires TLS; otherwise `false`
- `OPENAI_API_KEY` = optional, only if AI chatbot/recommendation feature uses it
- `OPENAI_MODEL` = `gpt-4.1-mini`

Deploy ke baad backend URL open karke `/admin/` ya `/api/catalog/` test karein. Admin login ke liye existing superuser use karein; zarurat ho to Render Shell mein `python manage.py createsuperuser` chalayein.

## 4) Render frontend Static Site
- New → Static Site → same GitHub repo.
- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Publish Directory: `dist`
- Environment variable: `VITE_API_URL` = `https://your-backend-name.onrender.com/api`

Frontend URL milne ke baad backend ke `CORS_ALLOWED_ORIGINS` aur `CSRF_TRUSTED_ORIGINS` ko exact frontend URL se update karke backend redeploy karein.

## 5) Cart migration + tech dataset
Backend deploy ke baad Render Shell mein:
```bash
python manage.py showmigrations cart
python manage.py migrate
python manage.py seed_tech_products
```
`seed_tech_products` repeat karne par duplicate products create nahi karta. Existing catalogue records delete nahi hote. Dataset demo inventory hai; real sales se pehle price, stock, descriptions aur image licensing verify karein.

## Important data persistence notes
- MySQL database mein users, products, carts, orders aur payments persist honge, jab tak external MySQL provider ka database active rahe. Render web service sleep/redeploy hone par MySQL data delete nahi hota.
- Render free web service idle hone par sleep kar sakti hai; first request slow ho sakti hai.
- App ke uploaded media (`backend/media`) Render filesystem par by default persistent nahi hain. Payment QR/product uploads ke liye persistent object storage ya supported persistent disk configure karein. External image URLs dataset ke liye use ho rahe hain.
- ZIP mein deployment configuration/fixes hain; isse GitHub par push ya Render par deploy automatically nahi hua.

## Safety checklist before live payments
UPI/QR and order-payment verification manually test karein. Demo product dataset ko verified inventory na samjhein. Real customer orders accept karne se pehle payment, stock, email, admin permissions, backups aur privacy/security checks complete karein.
