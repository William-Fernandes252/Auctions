# Generated by Django 4.0.2 on 2022-03-27 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_bid_options_rename_bid_value_bid_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='value',
            field=models.DecimalField(decimal_places=2, max_digits=9),
        ),
    ]
