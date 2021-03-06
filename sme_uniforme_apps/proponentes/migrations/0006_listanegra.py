# Generated by Django 2.2.9 on 2020-01-22 23:46

import django.core.validators
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('proponentes', '0005_auto_20200121_1508'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListaNegra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('cnpj', models.CharField(blank=True, default='', max_length=20, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='Digite CNPJ no formato XX.XXX.XXX/XXXX-XX.', regex='(^\\d{2}\\.\\d{3}\\.\\d{3}\\/\\d{4}\\-\\d{2}$)')], verbose_name='CNPJ')),
                ('razao_social', models.CharField(blank=True, max_length=255, null=True, verbose_name='Razão Social')),
            ],
            options={
                'verbose_name': 'CNPJ bloqueado',
                'verbose_name_plural': "CNPJ's bloqueados",
            },
        ),
    ]
