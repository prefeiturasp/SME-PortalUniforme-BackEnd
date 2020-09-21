# Generated by Django 2.2.9 on 2020-09-18 21:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('proponentes', '0023_loja_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='proponente',
            name='usuario',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]