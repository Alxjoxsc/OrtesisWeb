# Generated by Django 5.1 on 2024-10-16 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terapeuta', '0015_merge_0007_observacion_0014_cita_tipo_cita'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cita',
            name='tipo_cita',
        ),
        migrations.AddField(
            model_name='terapeuta',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
