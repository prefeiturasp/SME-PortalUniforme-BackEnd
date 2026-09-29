from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("proponentes", "0032_tipodocumento_identificador"),
    ]

    operations = [
        migrations.AddField(
            model_name="anexo",
            name="justificativa_ia",
            field=models.TextField(
                blank=True, null=True, verbose_name="Justificativa IA"
            ),
        ),
        migrations.AddField(
            model_name="anexo",
            name="status_ia",
            field=models.CharField(
                blank=True,
                choices=[
                    ("APROVADO", "Aprovado"),
                    ("REPROVADO", "Reprovado"),
                    ("PENDENTE", "Pendente"),
                    ("VENCIDO", "Vencido"),
                ],
                max_length=15,
                null=True,
                verbose_name="Status IA",
            ),
        ),
        migrations.AddField(
            model_name="anexo",
            name="ultima_alteracao_admin_em",
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="anexo",
            name="ultima_alteracao_admin_por",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="anexos_alterados_no_admin",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="anexo",
            name="justificativa",
            field=models.TextField(
                blank=True, null=True, verbose_name="Justificativa Admin"
            ),
        ),
        migrations.AlterField(
            model_name="anexo",
            name="status",
            field=models.CharField(
                choices=[
                    ("APROVADO", "Aprovado"),
                    ("REPROVADO", "Reprovado"),
                    ("PENDENTE", "Pendente"),
                    ("VENCIDO", "Vencido"),
                ],
                default="PENDENTE",
                max_length=15,
                verbose_name="Status Admin",
            ),
        ),
    ]
