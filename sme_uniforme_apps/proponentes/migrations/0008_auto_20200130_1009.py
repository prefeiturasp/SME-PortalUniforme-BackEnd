# Generated by Django 2.2.9 on 2020-01-30 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proponentes', '0007_proponente_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loja',
            name='numero',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Numero'),
        ),
    ]
