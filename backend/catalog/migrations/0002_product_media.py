from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('catalog', '0001_initial')]
    operations = [
        migrations.AlterField(model_name='product', name='image_url', field=models.URLField(blank=True)),
        migrations.AddField(model_name='product', name='image', field=models.ImageField(blank=True, null=True, upload_to='products/')),
    ]
