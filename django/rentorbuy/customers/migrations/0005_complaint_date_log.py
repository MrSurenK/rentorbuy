# Generated by Django 4.2.4 on 2023-09-04 07:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0004_complaint'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='date_log',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
