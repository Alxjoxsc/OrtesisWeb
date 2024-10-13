# Generated by Django 5.1 on 2024-10-11 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terapeuta', '0011_remove_terapeuta_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='sesion',
            name='estado',
            field=models.CharField(choices=[('Pendiente', 'Pendiente'), ('Realizada', 'Realizada'), ('Cancelada', 'Cancelada')], default='Pendiente', max_length=50),
        ),
    ]