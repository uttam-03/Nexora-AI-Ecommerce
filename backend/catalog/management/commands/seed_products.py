from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Category, Product, ProductSpecification

DATA = [
    ("Laptops","laptops","Apple","MacBook Air M3",89999,"https://images.unsplash.com/photo-1517336714739-489689fd1ca8"),
    ("Laptops","laptops","ASUS","ROG Gaming Laptop",74999,"https://images.unsplash.com/photo-1593642702749-b7d2a804fbcf"),
    ("Smartphones","smartphones","Samsung","Galaxy S Series",69999,"https://images.unsplash.com/photo-1511707171634-5f897ff02aa9"),
    ("Headphones & Audio","audio","Sony","WH Series Headphones",9999,"https://images.unsplash.com/photo-1505740420928-5e560c06d30e"),
    ("Gaming","gaming","Logitech","G Pro Gaming Mouse",4999,"https://images.unsplash.com/photo-1527814050087-3793815479db"),
    ("Monitors","monitors","LG","UltraGear Gaming Monitor",24999,"https://images.unsplash.com/photo-1527443224154-c4a3942d3acf"),
    ("Cameras","cameras","Canon","Mirrorless Camera",62999,"https://images.unsplash.com/photo-1516035069371-29a1b244cc32"),
    ("Smart Home","smart-home","Amazon","Echo Smart Speaker",4499,"https://images.unsplash.com/photo-1543512214-318c7553f230"),
    ("PC Components","pc-components","NVIDIA","GeForce Graphics Card",54999,"https://images.unsplash.com/photo-1591488320449-011701bb6704"),
    ("Accessories","accessories","Anker","USB-C Hub",2999,"https://images.unsplash.com/photo-1625842268584-8f3296236761"),
]

class Command(BaseCommand):
    help = "Add starter products without deleting or resetting existing data."

    def handle(self, *args, **kwargs):
        for category_name, cat_slug, brand, name, price, image in DATA:
            category, _ = Category.objects.get_or_create(slug=cat_slug, defaults={"name": category_name})
            slug = slugify(f"{brand}-{name}")
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "category": category, "brand": brand, "name": name,
                    "description": f"{brand} {name} — technology product available on Nexora.",
                    "price": price, "discount_price": None, "stock": 25,
                    "rating": 4.5, "review_count": 12, "image_url": image,
                    "is_active": True, "is_featured": True, "is_trending": True,
                }
            )
            self.stdout.write(self.style.SUCCESS(("Created: " if created else "Exists: ") + product.name))
        self.stdout.write(self.style.SUCCESS("Seed complete. Existing records were NOT deleted."))
