# Generated by Django 3.0 on 2019-12-17 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_category_productform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productform',
            name='price',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='productform',
            name='stock',
            field=models.PositiveIntegerField(),
        ),
    ]
