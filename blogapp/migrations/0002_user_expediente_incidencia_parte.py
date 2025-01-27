# Generated by Django 5.0.6 on 2024-07-02 09:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogapp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='expediente',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Incidencia',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_incidencia', models.CharField(max_length=10, null=True)),
                ('fecha_reporte', models.CharField(max_length=10, null=True)),
                ('referencia_articulo', models.IntegerField(null=True)),
                ('nombre_articulo', models.CharField(max_length=255, null=True)),
                ('numero_pedido', models.IntegerField(null=True)),
                ('unidades_totales_pedido', models.IntegerField(null=True)),
                ('unidades_mal_marcadas_revisadas', models.IntegerField(null=True)),
                ('coste_incidencia', models.IntegerField(null=True)),
                ('tecnica_marcado', models.CharField(max_length=255, null=True)),
                ('responsable_turno', models.CharField(max_length=255, null=True)),
                ('personas_implicadas', models.CharField(max_length=255, null=True)),
                ('persona_quien_detecta_error', models.CharField(max_length=255, null=True)),
                ('testigos', models.CharField(max_length=255, null=True)),
                ('observaciones', models.CharField(max_length=255, null=True)),
                ('creador', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('operario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incidencias', to='blogapp.user')),
            ],
        ),
        migrations.CreateModel(
            name='Parte',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('numero_pedido', models.IntegerField(null=True)),
                ('numero_fabricacion', models.IntegerField(null=True)),
                ('unidades', models.IntegerField(null=True)),
                ('observacion', models.CharField(max_length=255, null=True)),
                ('observacion_responsable', models.CharField(max_length=255, null=True)),
                ('observacion_operario', models.CharField(max_length=255, null=True)),
                ('maquina', models.CharField(max_length=255, null=True)),
                ('motivo', models.CharField(max_length=255, null=True)),
                ('accion', models.CharField(max_length=255, null=True)),
                ('creador', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('operario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partes', to='blogapp.user')),
            ],
        ),
    ]
