# Generated by Django 5.1 on 2024-10-08 21:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('terapeuta', '0010_sesion_angulo_max_sesion_angulo_min_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='terapeuta',
            name='estado',
        ),
    ]