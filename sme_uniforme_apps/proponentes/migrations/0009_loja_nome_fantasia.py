# Generated by Django 2.2.9 on 2020-02-04 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proponentes', '0008_auto_20200130_1009'),
    ]

    operations = [
        migrations.AddField(
            model_name='loja',
            name='nome_fantasia',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]