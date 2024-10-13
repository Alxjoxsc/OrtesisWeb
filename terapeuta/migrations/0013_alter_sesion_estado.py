# Generated by Django 5.1 on 2024-10-11 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terapeuta', '0012_sesion_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sesion',
            name='estado',
            field=models.CharField(choices=[('Pendiente', 'Pendiente'), ('Realizada', 'Realizada')], default='Pendiente', max_length=50),
        ),
    ]