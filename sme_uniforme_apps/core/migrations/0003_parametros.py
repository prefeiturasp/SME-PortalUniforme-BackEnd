# Generated by Django 2.2.9 on 2020-02-07 14:11

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_meioderecebimento'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parametros',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('edital', models.FileField(upload_to='')),
            ],
            options={
                'verbose_name': 'Parâmetro',
                'verbose_name_plural': 'Parâmetros',
            },
        ),
    ]