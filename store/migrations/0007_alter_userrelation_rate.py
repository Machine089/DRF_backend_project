# Generated by Django 4.1.4 on 2023-01-30 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_product_viewers_alter_product_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrelation',
            name='rate',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Bullshit'), (2, 'Bad'), (3, 'Normal'), (4, 'Good'), (5, 'Well')], null=True),
        ),
    ]