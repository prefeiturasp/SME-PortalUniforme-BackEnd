# Generated by Django 2.2.9 on 2020-09-08 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proponentes', '0022_merge_20200702_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='loja',
            name='site',
            field=models.URLField(blank=True, null=True),
        ),
    ]
