# Initial migration for installations that have not used syncdb for this app.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("catalog", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="UserInteraction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("interaction_type", models.CharField(choices=[("VIEW", "View"), ("WISHLIST", "Wishlist"), ("CART", "Cart"), ("PURCHASE", "Purchase"), ("SEARCH", "Search"), ("DISMISS", "Not interested")], max_length=20)),
                ("query", models.CharField(blank=True, max_length=250)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("product", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="catalog.product")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="interactions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="userinteraction", index=models.Index(fields=["user", "created_at"], name="rec_user_created_idx")),
        migrations.AddIndex(model_name="userinteraction", index=models.Index(fields=["product", "interaction_type"], name="rec_product_type_idx")),
    ]
