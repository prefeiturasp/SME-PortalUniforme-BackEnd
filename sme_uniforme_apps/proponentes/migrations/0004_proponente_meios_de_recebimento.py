# Generated by Django 2.2.9 on 2020-01-18 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_meioderecebimento'),
        ('proponentes', '0003_anexo'),
    ]

    operations = [
        migrations.AddField(
            model_name='proponente',
            name='meios_de_recebimento',
            field=models.ManyToManyField(related_name='proponentes_que_aceitam', to='core.MeioDeRecebimento'),
        ),
    ]