# Generated by Django 4.1.4 on 2023-02-17 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_alter_product_add_in_favorites'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='add_in_favorites',
            field=models.IntegerField(null=True),
        ),
    ]
