# Generated by Django 5.2 on 2025-06-25 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payments',
            name='razorpay_payment_id',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='payments',
            name='razorpay_signature',
            field=models.CharField(default='', max_length=200),
        ),
    ]
