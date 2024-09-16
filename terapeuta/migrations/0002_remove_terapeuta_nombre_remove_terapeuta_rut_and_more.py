# Generated by Django 5.1 on 2024-09-14 23:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terapeuta', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='terapeuta',
            name='nombre',
        ),
        migrations.RemoveField(
            model_name='terapeuta',
            name='rut',
        ),
        migrations.AddField(
            model_name='terapeuta',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
