# Generated by Django 5.1 on 2024-09-12 03:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terapeuta', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=50)),
                ('fecha', models.DateField()),
                ('hora', models.TimeField()),
                ('sala', models.CharField(max_length=50)),
                ('detalle', models.CharField(max_length=100)),
                ('id_terapeuta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='terapeuta.terapeuta')),
            ],
        ),
    ]
