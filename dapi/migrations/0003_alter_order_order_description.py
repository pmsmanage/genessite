# Generated by Django 4.1.7 on 2023-03-21 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dapi', '0002_remove_product_product_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_description',
            field=models.CharField(blank=True, default='', max_length=20000),
            preserve_default=False,
        ),
    ]
