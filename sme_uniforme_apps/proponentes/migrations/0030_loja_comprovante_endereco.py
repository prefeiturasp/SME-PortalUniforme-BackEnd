# Generated by Django 2.2.9 on 2022-02-15 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proponentes', '0029_tipodocumento_obrigatorio_sme'),
    ]

    operations = [
        migrations.AddField(
            model_name='loja',
            name='comprovante_endereco',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Comprovante de Endereço'),
        ),
    ]
