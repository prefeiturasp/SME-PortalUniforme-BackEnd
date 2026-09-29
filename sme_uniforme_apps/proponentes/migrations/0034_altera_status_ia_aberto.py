from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proponentes", "0033_anexo_campos_ia_e_auditoria"),
    ]

    operations = [
        migrations.AlterField(
            model_name="anexo",
            name="status_ia",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Status IA"
            ),
        ),
    ]
