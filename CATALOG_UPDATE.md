# Catalogue and Category Update

This update adds customer-facing category browsing and expands the starter/demo catalogue.

## What changed
- Shop page fetches active categories from `/api/catalog/categories/` and renders category filter chips.
- Selecting a category filters products through `category__slug`.
- Product cards display category name and brand.
- Product catalogue endpoint accepts `page_size` (maximum 200) so the expanded starter catalogue can be displayed in one request.
- Starter seed now includes 13 categories and 116+ demo product listings, with baseline specification rows.
- Existing products, categories, users, orders and recommendation data are not deleted.

## Apply the catalogue update
From the backend folder, with the virtual environment active and database configured:

```powershell
python manage.py check
python manage.py seed_products
```

No migration is required for this category/dataset update. The seed command is safe to run more than once: it uses `get_or_create` and does not overwrite existing products.

## Important catalogue note
The added records are starter/demo listings intended to populate and test the storefront. Verify exact model variants, prices, images, availability and technical specifications before accepting real customer orders. Replace generic/demo information with verified inventory from the admin dashboard.
