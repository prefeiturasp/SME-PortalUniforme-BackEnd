# Generated by Django 2.2.9 on 2020-02-20 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proponentes', '0015_auto_20200219_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proponente',
            name='status',
            field=models.CharField(choices=[('INSCRITO', 'Inscrito'), ('BLOQUEADO', 'Bloqueado'), ('EM_PROCESSO', 'Em processo')], default='EM_PROCESSO', max_length=15, verbose_name='status'),
        ),
    ]
