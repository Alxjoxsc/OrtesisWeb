# Generated by Django 5.1 on 2024-10-13 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terapeuta', '0013_alter_sesion_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='terapeuta',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
