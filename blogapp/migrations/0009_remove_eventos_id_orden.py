# Generated by Django 5.0.6 on 2024-07-12 15:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blogapp', '0008_eventos_id_orden'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventos',
            name='id_orden',
        ),
    ]
