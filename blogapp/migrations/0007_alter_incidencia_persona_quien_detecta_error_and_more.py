# Generated by Django 5.0.6 on 2024-07-12 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogapp', '0006_alter_incidencia_observaciones_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incidencia',
            name='persona_quien_detecta_error',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='incidencia',
            name='personas_implicadas',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='incidencia',
            name='responsable_turno',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='incidencia',
            name='testigos',
            field=models.TextField(blank=True, null=True),
        ),
    ]