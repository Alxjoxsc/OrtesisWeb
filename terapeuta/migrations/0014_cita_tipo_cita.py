# Generated by Django 5.1 on 2024-10-14 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terapeuta', '0013_alter_sesion_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='cita',
            name='tipo_cita',
            field=models.CharField(choices=[('Presencial', 'Presencial'), ('Online', 'Online')], default='Presencial', max_length=50),
        ),
    ]
