import json
import os
from django.core.management.base import BaseCommand
from autenticacion.models import Region, Comuna

class Command(BaseCommand):
    help = 'Carga datos desde un archivo JSON a la base de datos'

    def handle(self, *args, **kwargs):
        # Ruta fija al archivo JSON
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/datos_geograficos1.json')

        # Verifica si el archivo existe
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f'El archivo {json_path} no existe'))
            return
        
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Itera sobre los datos y guarda en la base de datos
            for region_data in data:
                region, created = Region.objects.get_or_create(nombre=region_data['region'])
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Región creada: {region.nombre}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Región existente: {region.nombre}'))

                # Asumiendo que ahora 'comunas' está directamente bajo la región
                for comuna_data in region_data['comunas']:
                    comuna, created = Comuna.objects.get_or_create(nombre=comuna_data['name'], region=region)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Comuna creada: {comuna.nombre}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Comuna existente: {comuna.nombre}'))

            self.stdout.write(self.style.SUCCESS("Datos cargados exitosamente."))
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Error al leer el archivo JSON: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al cargar datos: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
