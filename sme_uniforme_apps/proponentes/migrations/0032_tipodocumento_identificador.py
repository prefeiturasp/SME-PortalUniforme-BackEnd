from django.core.validators import RegexValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("proponentes", "0031_auto_20220215_1457"),
    ]

    operations = [
        migrations.AddField(
            model_name="tipodocumento",
            name="identificador",
            field=models.CharField(
                blank=True,
                help_text="Use apenas letras, números, hífen e underscore.",
                max_length=100,
                null=True,
                unique=True,
                validators=[
                    RegexValidator(
                        message="Use apenas letras, números, hífen e underscore.",
                        regex="^[0-9A-Za-z_-]+$",
                    )
                ],
                verbose_name="Identificador",
            ),
        ),
    ]
