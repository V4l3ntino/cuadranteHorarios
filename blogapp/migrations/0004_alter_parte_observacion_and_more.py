# Generated by Django 5.0.6 on 2024-07-05 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogapp', '0003_parte_fecha_reporte'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parte',
            name='observacion',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='parte',
            name='observacion_operario',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='parte',
            name='observacion_responsable',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
