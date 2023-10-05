# Generated by Django 4.1.7 on 2023-03-21 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dapi', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='product_type',
        ),
        migrations.AlterField(
            model_name='product',
            name='product_description',
            field=models.CharField(blank=True, default='', max_length=20000),
        ),
    ]