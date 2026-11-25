NEXORA AI E-COMMERCE - TECHNOLOGY DATASET PATCH

Contains 250 technology product demo records across technology categories, with category, brand, price, stock, image URL and up to six specifications per product.

INSTALL:
1. Extract this ZIP.
2. Copy the included backend/catalog/data/ folder into your project's backend/catalog/data/ folder.
3. Copy backend/catalog/management/commands/seed_tech_products.py into your project's backend/catalog/management/commands/ folder. Keep existing __init__.py files.
4. From the backend folder, activate your existing virtual environment and run:

   python manage.py check
   python manage.py seed_tech_products

This command is additive and idempotent: it uses category slugs and product slugs to avoid duplicate imports. It does not delete or overwrite existing products. It adds specifications only when the matching product/specification key is not already present. It also refreshes existing products image_url values from the CSV while preserving all other product fields.

NOTES:
- These are demo catalogue records, not verified live inventory or current manufacturer listings.
- Product titles, descriptions, prices, stock and specifications must be reviewed before real sales.
- Image URLs are external Unsplash image references; internet access is needed for them to load. Replace with licensed product photos before production.
- No database reset or migration is required for this dataset command, assuming the Category, Product and ProductSpecification models match the Nexora schema.
