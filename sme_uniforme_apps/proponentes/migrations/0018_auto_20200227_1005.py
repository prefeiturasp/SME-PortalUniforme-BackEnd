# Generated by Django 2.2.9 on 2020-02-27 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proponentes', '0017_tipodocumento_visivel'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='loja',
            options={'ordering': ('id',), 'verbose_name': 'Loja física', 'verbose_name_plural': 'Lojas físicas'},
        ),
    ]