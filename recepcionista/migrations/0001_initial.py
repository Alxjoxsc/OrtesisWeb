# Generated by Django 5.0.6 on 2024-09-24 22:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Recepcionista',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_contratacion', models.DateField()),
                ('turno', models.CharField(choices=[('M', 'Mañana'), ('T', 'Tarde'), ('N', 'Noche')], max_length=100, null=True)),
                ('experiencia', models.IntegerField(blank=True, null=True)),
                ('formacion_academica', models.CharField(max_length=100, null=True)),
                ('supervisor', models.BooleanField(default=False)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
