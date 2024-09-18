# Generated by Django 5.0.6 on 2024-07-11 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogapp', '0004_alter_parte_observacion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incidencia',
            name='fecha_incidencia',
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='incidencia',
            name='fecha_reporte',
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='parte',
            name='fecha_reporte',
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='parte',
            name='observacion',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='parte',
            name='observacion_operario',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='parte',
            name='observacion_responsable',
            field=models.CharField(max_length=255, null=True),
        ),
    ]