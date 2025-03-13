# Generated by Django 5.1.7 on 2025-03-10 07:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djstripe', '0014_2_9a'),
        ('users', '0003_artistrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='stripe_accounts',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='djstripe.account'),
        ),
        migrations.AddField(
            model_name='users',
            name='stripe_customer',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='djstripe.customer'),
        ),
    ]
