# Generated by Django 5.0.6 on 2024-07-12 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogapp', '0007_alter_incidencia_persona_quien_detecta_error_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventos',
            name='id_orden',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
