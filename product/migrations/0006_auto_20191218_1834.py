# Generated by Django 3.0 on 2019-12-18 18:34

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_auto_20191217_1906'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', tinymce.models.HTMLField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='productform',
            options={'verbose_name': 'Products', 'verbose_name_plural': 'Products'},
        ),
    ]
