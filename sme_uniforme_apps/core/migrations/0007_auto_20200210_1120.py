# Generated by Django 2.2.9 on 2020-02-10 14:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0006_limitecategoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='limitecategoria',
            name='categoria_uniforme',
            field=models.CharField(choices=[('MALHARIA', 'Vestuário'), ('CALCADO', 'Calçados')], default='MALHARIA',
                                   max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='uniforme',
            name='categoria',
            field=models.CharField(choices=[('MALHARIA', 'Vestuário'), ('CALCADO', 'Calçados')], default='MALHARIA',
                                   max_length=10),
        ),
    ]
