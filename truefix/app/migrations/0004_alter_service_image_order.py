# Generated by Django 5.1.2 on 2025-03-01 06:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_category_remove_payment_appointment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='image',
            field=models.ImageField(null=True, upload_to='services/'),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(verbose_name='Account')),
                ('status', models.CharField(default='pending', max_length=254, verbose_name='Payment_Status')),
                ('provider_order_id', models.CharField(max_length=40, verbose_name='order ID')),
                ('payment_id', models.CharField(max_length=36, verbose_name='order ID')),
                ('signature_id', models.CharField(max_length=128, verbose_name='order ID')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.booking')),
            ],
        ),
    ]
