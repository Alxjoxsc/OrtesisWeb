# Generated by Django 5.1 on 2024-10-08 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terapeuta', '0009_remove_sesion_corriente_corriente'),
    ]

    operations = [
        migrations.AddField(
            model_name='sesion',
            name='angulo_max',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sesion',
            name='angulo_min',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sesion',
            name='repeticiones',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sesion',
            name='velocidad',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
