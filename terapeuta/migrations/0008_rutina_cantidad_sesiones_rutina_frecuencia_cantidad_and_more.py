# Generated by Django 5.1 on 2024-11-15 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terapeuta', '0007_cita_tipo_cita'),
    ]

    operations = [
        migrations.AddField(
            model_name='rutina',
            name='cantidad_sesiones',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='rutina',
            name='frecuencia_cantidad',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='rutina',
            name='frecuencia_tipo',
            field=models.CharField(choices=[('día', 'día'), ('semana', 'semana')], default='día', max_length=50),
        ),
    ]