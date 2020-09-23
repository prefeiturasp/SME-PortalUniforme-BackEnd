# Generated by Django 2.2.9 on 2020-09-22 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proponentes', '0025_proponente_observacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proponente',
            name='status',
            field=models.CharField(choices=[('INSCRITO', 'Inscrito'), ('BLOQUEADO', 'Bloqueado'), ('EM_PROCESSO', 'Pré-cadastro'), ('APROVADO', 'Aprovado'), ('REPROVADO', 'Reprovado'), ('PENDENTE', 'Pendente'), ('EM_ANALISE', 'Em análise'), ('CREDENCIADO', 'Credenciado'), ('DESCREDENCIADO', 'Descredenciado'), ('ALTERADO', 'Alterado')], default='EM_PROCESSO', max_length=15, verbose_name='status'),
        ),
    ]
