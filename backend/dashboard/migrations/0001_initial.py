from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial=True
    dependencies=[('catalog','0001_initial'),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.CreateModel(name='ProductReview',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('rating',models.PositiveSmallIntegerField()),('title',models.CharField(blank=True,max_length=160)),('comment',models.TextField()),('is_visible',models.BooleanField(default=True)),('created_at',models.DateTimeField(auto_now_add=True)),('product',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='customer_reviews',to='catalog.product')),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='product_reviews',to=settings.AUTH_USER_MODEL))],options={'ordering':['-created_at']}),
        migrations.CreateModel(name='CustomerFeedback',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('feedback_type',models.CharField(choices=[('COMPLAINT','Complaint'),('FEEDBACK','Feedback'),('SERVICE','Service issue')],default='FEEDBACK',max_length=20)),('subject',models.CharField(max_length=180)),('message',models.TextField()),('status',models.CharField(choices=[('OPEN','Open'),('IN_PROGRESS','In progress'),('RESOLVED','Resolved'),('CLOSED','Closed')],default='OPEN',max_length=20)),('admin_response',models.TextField(blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('product',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='feedback',to='catalog.product')),('seller',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='seller_feedback',to=settings.AUTH_USER_MODEL)),('user',models.ForeignKey(null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='submitted_feedback',to=settings.AUTH_USER_MODEL))],options={'ordering':['-created_at']}),
        migrations.AddConstraint(model_name='productreview',constraint=models.UniqueConstraint(fields=('user','product'),name='one_review_per_user_product')),
    ]
