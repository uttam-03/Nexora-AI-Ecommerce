import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ('accounts', '0003_alter_user_managers'), ('catalog', '0002_product_media')]
    operations = [
        migrations.CreateModel(name='Order', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('status', models.CharField(choices=[('PLACED','Placed'),('CONFIRMED','Confirmed'),('SHIPPED','Shipped'),('OUT_FOR_DELIVERY','Out for delivery'),('DELIVERED','Delivered'),('CANCELLED','Cancelled')], default='PLACED', max_length=30)), ('payment_method', models.CharField(choices=[('COD','Cash on Delivery'),('ONLINE','Online')], default='COD', max_length=20)), ('payment_reference', models.CharField(blank=True, max_length=150)), ('total', models.DecimalField(decimal_places=2, default=0, max_digits=14)), ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)), ('address', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.address')), ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to=settings.AUTH_USER_MODEL))]),
        migrations.CreateModel(name='OrderItem', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('product_name', models.CharField(max_length=200)), ('unit_price', models.DecimalField(decimal_places=2, max_digits=12)), ('quantity', models.PositiveIntegerField(default=1)), ('line_total', models.DecimalField(decimal_places=2, max_digits=14)), ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order')), ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='catalog.product'))]),
    ]
