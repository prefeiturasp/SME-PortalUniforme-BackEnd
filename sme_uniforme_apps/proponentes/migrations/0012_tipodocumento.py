# Generated by Django 2.2.9 on 2020-02-05 16:10

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('proponentes', '0011_remove_proponente_meios_de_recebimento'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoDocumento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('nome', models.CharField(max_length=100, unique=True, verbose_name='Tipo de documento')),
                ('obrigatorio', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Tipo de documento',
                'verbose_name_plural': 'Tipos de documentos',
            },
        ),
    ]
