# Generated by Django 3.0 on 2019-12-17 18:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('superCategory', models.IntegerField(choices=[(1, 'Electronics'), (2, 'Clothing'), (3, 'Home & Kitchen'), (4, 'Footwear'), (5, 'More')], default=1)),
                ('description', models.Field(max_length=1000)),
                ('categoryIcon', models.ImageField(upload_to='category_images/')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='ProductForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('description', models.CharField(max_length=1000)),
                ('price', models.IntegerField()),
                ('uploadedDate', models.DateTimeField(auto_now=True)),
                ('stock', models.IntegerField()),
                ('image', models.ImageField(upload_to='product_images/')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='product.Category')),
            ],
        ),
    ]
