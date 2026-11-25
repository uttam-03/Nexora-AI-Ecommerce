import csv
import hashlib
from decimal import Decimal
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Category, Product, ProductSpecification

class Command(BaseCommand):
    help = "Import 250 technology demo products without deleting existing catalogue data."

    def handle(self, *args, **options):
        csv_path = Path(__file__).resolve().parents[2] / "data" / "nexora_technology_products.csv"
        created_categories = created_products = existing_products = created_specs = 0
        with csv_path.open(newline="", encoding="utf-8-sig") as file:
            for row in csv.DictReader(file):
                category, category_created = Category.objects.get_or_create(
                    slug=row["category_slug"],
                    defaults={"name": row["category"], "image_url": row["category_image"], "is_active": True},
                )
                if category_created:
                    created_categories += 1
                elif not category.image_url and row.get("category_image"):
                    category.image_url = row["category_image"]
                    category.save(update_fields=["image_url"])

                raw_slug = row["slug"] or slugify(f'{row["brand"]}-{row["name"]}')
                slug_limit = Product._meta.get_field("slug").max_length or 50
                if len(raw_slug) > slug_limit:
                    suffix = hashlib.sha1(raw_slug.encode("utf-8")).hexdigest()[:8]
                    slug = f"{raw_slug[:slug_limit - 9].rstrip('-')}-{suffix}"
                else:
                    slug = raw_slug
                product, was_created = Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "category": category,
                        "brand": row["brand"],
                        "name": row["name"],
                        "description": row["description"],
                        "price": Decimal(row["price"]),
                        "stock": int(row["stock"] or 0),
                        "rating": Decimal("4.2"),
                        "review_count": 0,
                        "image_url": row.get("image_url", ""),
                        "is_active": True,
                        "is_featured": False,
                        "is_trending": False,
                    },
                )
                if was_created:
                    created_products += 1
                else:
                    existing_products += 1
                    # Refresh only the image URL; preserve all other existing product data.
                    new_image_url = row.get("image_url", "")
                    if new_image_url and product.image_url != new_image_url:
                        product.image_url = new_image_url
                        product.save(update_fields=["image_url", "updated_at"])

                for index in range(1, 7):
                    key = row.get(f"spec_{index}_key", "").strip()
                    value = row.get(f"spec_{index}_value", "").strip()
                    if key and value:
                        _, made = ProductSpecification.objects.get_or_create(
                            product=product, key=key, defaults={"value": value}
                        )
                        created_specs += int(made)

        self.stdout.write(self.style.SUCCESS(
            f"Tech dataset imported. New categories: {created_categories}; "
            f"new products: {created_products}; already present: {existing_products}; "
            f"new specifications: {created_specs}. Existing records were preserved."
        ))
