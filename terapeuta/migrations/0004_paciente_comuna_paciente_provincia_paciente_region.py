# Generated by Django 5.1 on 2024-09-30 04:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autenticacion', '0001_initial'),
        ('terapeuta', '0003_alter_paciente_date_joined'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='comuna',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='autenticacion.comuna'),
        ),
        migrations.AddField(
            model_name='paciente',
            name='provincia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='autenticacion.provincia'),
        ),
        migrations.AddField(
            model_name='paciente',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='autenticacion.region'),
        ),
    ]