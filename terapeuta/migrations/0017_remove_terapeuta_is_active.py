# Generated by Django 5.1 on 2024-10-16 02:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('terapeuta', '0016_remove_cita_tipo_cita_terapeuta_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='terapeuta',
            name='is_active',
        ),
    ]
