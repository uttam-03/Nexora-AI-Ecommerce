from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("accounts", "0003_alter_user_managers")]
    operations = [
        migrations.AddField(model_name="user", name="address_line", field=models.CharField(blank=True, max_length=250)),
        migrations.AddField(model_name="user", name="city", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="user", name="state", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="user", name="postal_code", field=models.CharField(blank=True, max_length=20)),
    ]
