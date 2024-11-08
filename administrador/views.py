import json
import re
import csv
import pandas as pd
from decimal import Decimal
from datetime import date
from itertools import cycle
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from autenticacion.decorators import role_required
from .forms import CrearTerapeutaForm, HorarioFormSet, CrearPacienteForm, EditarPacienteForm
from autenticacion.models import Provincia, Comuna, Region
from django.http import HttpResponse, JsonResponse
from terapeuta.models import Paciente, Terapeuta, Cita, Horario
from recepcionista.models import Recepcionista
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages

############################### LISTAR TERAPEUTAS ################################
@role_required('Administrador')
def listar_terapeutas_activos(request): 
    query = request.GET.get('search')
    order_by = request.GET.get('order_by', 'user__first_name')
    terapeutas_list = Terapeuta.objects.filter(user__is_active=True)

    # Aplicar el filtro de búsqueda
    if query:
        terapeutas_list = terapeutas_list.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__profile__rut__icontains=query) |  # Asumiendo que 'rut' está en el perfil
            Q(especialidad__icontains=query)
        )

    # Aplicar el filtro de orden
    if order_by:
        terapeutas_list = terapeutas_list.order_by(order_by)
    
    # Paginación
    paginator = Paginator(terapeutas_list, 5)
    page_number = request.GET.get('page')
    terapeutas = paginator.get_page(page_number)

    return render(request, 'admin_terapeutas.html', {
        'terapeutas': terapeutas,
        'estado': 'activos',
        'query': query,  # Para mantener el valor en el HTML
        'order_by': order_by,  # Para saber el orden actual en el HTML
        'modulo_terapeutas': True
    })

@role_required('Administrador')
def listar_terapeutas_inactivos(request):
    query = request.GET.get('search')
    order_by = request.GET.get('order_by', 'user__first_name')
    terapeutas_list = Terapeuta.objects.filter(user__is_active=False)

    if query:
        terapeutas_list = terapeutas_list.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__profile__rut__icontains=query) |
            Q(especialidad__icontains=query)
        )
    
    if order_by:
        terapeutas_list = terapeutas_list.order_by(order_by)
    
    paginator = Paginator(terapeutas_list, 5)
    page_number = request.GET.get('page')
    terapeutas = paginator.get_page(page_number)

    return render(request, 'admin_terapeutas.html', {
        'terapeutas': terapeutas,
        'estado': 'inactivos',
        'query': query,  # Para mantener el valor en el HTML
        'order_by': order_by,  # Para saber el orden actual en el HTML
        'modulo_terapeutas': True
    })

@role_required('Administrador')
def cambiar_estado_inactivo_terapeuta(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        terapeutas_ids = data.get('terapeutas_ids', [])
        
        # Obtener el queryset de los terapeutas antes de actualizar su estado
        terapeutas = Terapeuta.objects.filter(id__in=terapeutas_ids)

        # Cambiar el estado de los terapeutas a inactivo
        for terapeuta in terapeutas:
            terapeuta.user.is_active = False
            terapeuta.user.save()
        
        return JsonResponse({
            'status': 'success',
            'terapeutas_afectados': [terapeuta.id for terapeuta in terapeutas]
        })

@role_required('Administrador')
def restaurar_terapeuta(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        terapeutas_ids = data.get('terapeutas_ids', [])
        
        # Obtener el queryset de los terapeutas a restaurar
        terapeutas = Terapeuta.objects.filter(id__in=terapeutas_ids)
        
        # Restaurar el estado de los terapeutas a activo
        for terapeuta in terapeutas:
            terapeuta.user.is_active = True
            terapeuta.user.save()
        
        return JsonResponse({
            'status': 'success',
            'terapeutas_restaurados': [terapeuta.id for terapeuta in terapeutas]
        })

################### ADMIN PACIENTES ##################
@role_required('Administrador')
def agregar_paciente_admin(request):
    success = False
    if request.method == 'POST':
        form = CrearPacienteForm(request.POST)
        if form.is_valid():
            # Guarda el nuevo paciente y almacena el objeto en 'paciente'
            paciente = form.save()  # Esto devuelve el objeto paciente creado
            success = True
            return redirect('mostrar_paciente_administrador', paciente_id=paciente.id)
    else:
        form = CrearPacienteForm()
        
    return render(request, 'agregar_paciente_admin.html', {
        'paciente_form': form,
        'success': success,
        'modulo_pacientes': True,
    })

@role_required('Administrador')
def elegir_terapeuta_administrador(request, paciente_id):
    paciente = Paciente.objects.get(id=paciente_id)
    terapeuta = Terapeuta.objects.all()
    return render(request, 'elegir_terapeuta_administrador.html', {
        'terapeuta': terapeuta, 
        'paciente': paciente,
        'modulo_pacientes': True,})

@role_required('Administrador')
def asignar_terapeuta_administrador(request, terapeuta_id, paciente_id):
    # Obtener el paciente y el terapeuta, manejando el caso en que no existan
    paciente = get_object_or_404(Paciente, id=paciente_id)
    terapeuta = get_object_or_404(Terapeuta, id=terapeuta_id)

    # Obtener y eliminar todas las citas existentes del paciente
    citas_existentes = Cita.objects.filter(paciente=paciente)
    citas_existentes.delete()

    # Asignar el terapeuta al paciente
    paciente.terapeuta = terapeuta
    paciente.save()

    # Redirigir a la página de mostrar paciente
    return render(request, 'mostrar_paciente_administrador.html', {
        'paciente': paciente,
        'modulo_pacientes': True,})

@role_required('Administrador')
def mostrar_paciente_sin_terapeuta(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    edad = paciente.calcular_edad()
    imc = paciente.calcular_imc()
    cita = Cita.objects.filter(paciente_id=paciente_id).order_by('fecha').last()
    return render(request, 'mostrar_paciente_administrador.html', {'paciente': paciente, 'edad': edad, 'cita': cita, 'imc': imc, 'modulo_pacientes': True})

@role_required('Administrador')
def mostrar_paciente_con_terapeuta(request, paciente_id, terapeuta_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    terapeuta = Terapeuta.objects.get(id=terapeuta_id)
    edad = paciente.calcular_edad()
    imc = paciente.calcular_imc()
    cita = Cita.objects.filter(paciente_id=paciente_id).order_by('fecha').last()
    return render(request, 'mostrar_paciente_administrador.html', {'paciente': paciente, 'edad': edad, 'cita': cita, 'imc': imc, 'terapeuta':terapeuta, 'modulo_pacientes': True})

@role_required('Administrador')
def listar_pacientes_activos(request):
    query = request.GET.get('search')
    order_by = request.GET.get('order_by', 'first_name')
    pacientes_activos = Paciente.objects.filter(is_active=True)

    if query:

        if query.lower() == 'sin terapeuta':

            # Filtrar pacientes sin terapeuta
            pacientes_activos = pacientes_activos.filter(terapeuta__isnull=True)

        else:
            pacientes_activos = pacientes_activos.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(rut__icontains=query) |
                Q(terapeuta__user__first_name__icontains=query) |
                Q(terapeuta__user__last_name__icontains=query)
            )

    if order_by:
        pacientes_activos = pacientes_activos.order_by(order_by)
        
    paginator = Paginator(pacientes_activos, 5)
    page_number = request.GET.get('page')
    pacientes = paginator.get_page(page_number)

    return render(request, 'admin_pacientes.html', {
        'pacientes': pacientes,
        'estado': 'activos',
        'query': query,  # Para mantener el valor en el HTML
        'order_by': order_by,  # Para saber el orden actual en el HTML
        'modulo_pacientes': True
    })
    
@role_required('Administrador')
def cambiar_estado_inactivo(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pacientes_ids = data.get('pacientes_ids', [])
        
        # Obtener el queryset de los pacientes antes de actualizar su estado
        pacientes = Paciente.objects.filter(id__in=pacientes_ids)
        
        # Eliminar todas las citas de los pacientes afectados
        Cita.objects.filter(paciente__in=pacientes).delete()
        
        # Cambiar el estado de los pacientes a inactivo
        pacientes.update(is_active=False)
        
        # Ahora tienes las instancias de los pacientes afectados
        pacientes_afectados = list(pacientes)  # Puedes usarlas para lo que necesites
        
        return JsonResponse({
            'status': 'success',
            'pacientes_afectados': [paciente.id for paciente in pacientes_afectados]
        })



@role_required('Administrador')
def restaurar_paciente(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pacientes_ids = data.get('pacientes_ids', [])
        
        # Obtener el queryset de los pacientes a restaurar
        pacientes = Paciente.objects.filter(id__in=pacientes_ids)
        
        # Desasignar el terapeuta (poniendo terapeuta_id a None)
        pacientes.update(terapeuta_id=None)
        
        # Restaurar el estado de los pacientes a activo
        pacientes.update(is_active=True)
        
        return JsonResponse({
            'status': 'success',
            'pacientes_restaurados': [paciente.id for paciente in pacientes]
        })

    
@role_required('Administrador')
def listar_pacientes_inactivos(request):
    query = request.GET.get('search')
    order_by = request.GET.get('order_by', 'first_name')
    pacientes_inactivos = Paciente.objects.filter(is_active=False)

    if query:

        if query.lower() == 'sin terapeuta':

            # Filtrar pacientes sin terapeuta
            pacientes_inactivos = pacientes_inactivos.filter(terapeuta__isnull=True)

        else:
            pacientes_inactivos = pacientes_inactivos.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(rut__icontains=query) |
                Q(terapeuta__user__first_name__icontains=query) |
                Q(terapeuta__user__last_name__icontains=query)
            )
    
    if order_by:
        pacientes_inactivos = pacientes_inactivos.order_by(order_by)
    
    paginator = Paginator(pacientes_inactivos, 5)
    page_number = request.GET.get('page')
    pacientes = paginator.get_page(page_number)

    return render(request, 'admin_pacientes.html', {
        'pacientes': pacientes,
        'estado': 'inactivos',
        'query': query,  # Para mantener el valor en el HTML
        'order_by': order_by,  # Para saber el orden actual en el HTML
        'modulo_pacientes': True
    })

#                       CARGA MASIVA DE PACIENTES                     #

def archivo_csv_ejemplo(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="ejemplo_carga_masiva_paciente.csv"'
    response.write('\ufeff'.encode('utf8'))  # Escribe el BOM para UTF-8

    writer = csv.writer(response)
    
    writer.writerow([
        'Rut', 'Nombre', 'Apellido', 'Fecha Nacimiento', 'Sexo', 'Telefono', 
        'Email', 'Contacto Emergencia', 'Telefono Emergencia', 'Patologia', 
        'Descripcion Patologia', 'Medicamentos', 'Alergias', 'Actividad Fisica', 
        'Peso', 'Altura', 'Region', 'Provincia', 'Comuna', 'Calle'
    ])
    
    writer.writerow([
        '8.895.157-3', 'Exequiel', 'Hurtado', '1990-01-01', 'Masculino', '9 1234 5678', 
        'correo@example.com', 'Contacto Emergencia', '9 8765 4321', 'Diabetes', 
        'Descripcion de la patologia', 'Insulina', 'Penicilina', 'Activo', 
        '75.5', '1.78', '1', '1', '1', 'Calle falsa 123'
    ])
    
    return response

def carga_masiva_pacientes(request):
    registros_subidos = 0
    registros_no_subidos = 0
    registros_no_validos = []
    COLUMNAS_ESPERADAS = 20

    if request.method == 'POST':
        if 'archivo_csv' not in request.FILES:
            messages.error(request, 'No se subió ningún archivo')
            return redirect('listar_pacientes_activos')

        try:
            data = pd.read_csv(request.FILES['archivo_csv'], delimiter=',', encoding='utf-8')
            # Validación de la cantidad de columnas
            if len(data.columns) != COLUMNAS_ESPERADAS:
                messages.error(request, f'El archivo debe tener exactamente {COLUMNAS_ESPERADAS} columnas. '
                                        f'Se encontraron {len(data.columns)} columnas.')
                return redirect('listar_pacientes_activos')
            
        except pd.errors.ParserError:
            messages.error(request, 'El archivo no tiene el formato correcto')
            return redirect('listar_pacientes_activos')
        except Exception as e:
            messages.error(request, f'Error al leer el archivo: {str(e)}')
            return redirect('listar_pacientes_activos')

        fila = 0  # Variable para contar las filas (empezamos desde 1)
        for index, row in data.iterrows():
            fila += 1 # Incrementa el contador de filas
            errores = []  # Lista de errores para la fila actual
            
            try:
                
                # Validación de Rut
                rut = row['Rut']
                if not re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', rut):
                    errores.append(f'El RUT "{rut}" debe estar en el formato XX.XXX.XXX-X')
                
                # Validación de dígito verificador
                clean_rut = rut.replace(".", "").replace("-", "")
                num_part = clean_rut[:-1]
                dv = clean_rut[-1].upper()
                reversed_digits = map(int, reversed(num_part))
                factors = cycle(range(2, 8))
                s = sum(d * f for d, f in zip(reversed_digits, factors))
                verificador = 'K' if (-s) % 11 == 10 else str((-s) % 11)
                if dv != verificador:
                    errores.append(f'El dígito verificador del RUT "{rut}" no es válido')
                
                # Validación para el primer nombre, permite hasta 3 nombres con letras y caracteres especiales
                first_name = row['Nombre']
                if not re.match(r'^[a-zA-Z\u00C0-\u017F]+( [a-zA-Z\u00C0-\u017F]+){0,2}$', first_name):
                    errores.append(f'El nombre "{first_name}" solo puede contener letras y hasta 3 nombres separados por espacios')

                # Validación para el apellido, permite hasta 2 apellidos con letras y caracteres especiales
                last_name = row['Apellido']
                if not re.match(r'^[a-zA-Z\u00C0-\u017F]+( [a-zA-Z\u00C0-\u017F]+)?$', last_name):
                    errores.append(f'El apellido "{last_name}" solo puede contener letras y hasta 2 apellidos separados por un espacio')
                
                # Validación de correo electrónico
                email = row['Email']
                if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                    errores.append(f'El correo "{email}" no es válido')
                
                # Validación de teléfono
                telefono = row['Telefono']
                if not re.match(r'^\d{1} \d{4} \d{4}$', telefono):
                    errores.append(f'El teléfono "{telefono}" debe tener el formato: 9 1234 5678')
                
                # Validación de fecha de nacimiento
                fecha_nacimiento = pd.to_datetime(row['Fecha Nacimiento'], errors='coerce')
                if pd.isna(fecha_nacimiento) or fecha_nacimiento.date() >= date.today():
                    errores.append(f'La fecha de nacimiento "{row["Fecha Nacimiento"]}" debe ser anterior a la fecha actual')

                
                # Validación de sexo
                sexo = row['Sexo'].capitalize()
                if sexo not in ['Masculino', 'Femenino']:
                    errores.append(f'El sexo "{sexo}" debe ser "Masculino" o "Femenino"')
                
                contacto_emergencia = row['Contacto Emergencia']
                if not re.match(r'^[a-zA-Z\u00C0-\u017F]+( [a-zA-Z\u00C0-\u017F]+)?$', contacto_emergencia):
                    errores.append(f'El contacto de emergencia "{contacto_emergencia}" solo puede contener letras y un apellido opcional separados por un espacio')

                telefono_emergencia = row['Telefono Emergencia']
                if not re.match(r'^\d{1} \d{4} \d{4}$', telefono_emergencia):
                    errores.append(f'El teléfono de emergencia "{telefono_emergencia}" debe tener el formato: 9 1234 5678')
                
                patologia = row['Patologia']
                if not re.match(r'^[a-zA-Z\u00C0-\u017F ]+$', patologia):
                    errores.append(f'La patología "{patologia}" solo puede contener letras y espacios')

                
                descripcion_patologia = row['Descripcion Patologia']
                if not re.match(r'^[a-zA-Z\u00C0-\u017F ]+$', descripcion_patologia):
                    errores.append(f'La descripción de la patología "{descripcion_patologia}" solo puede contener letras y espacios')

                medicamentos = row['Medicamentos']
                if not re.match(r'^[a-zA-Z\u00C0-\u017F ]+$', str(medicamentos)):
                    errores.append(f'Los medicamentos "{medicamentos}" solo pueden contener letras y espacios')
                
                alergias = row['Alergias']
                if not re.match(r'^[a-zA-Z\u00C0-\u017F ]+$', str(alergias)):
                    errores.append(f'Las alergias "{alergias}" solo pueden contener letras y espacios')
                
                actividad_fisica = row['Actividad Fisica']
                if actividad_fisica not in ['Sedentario', 'Moderado', 'Activo']:
                    errores.append(f'La actividad física "{actividad_fisica}" debe ser "Sedentario", "Moderado" o "Activo"')

                calle = row['Calle']
                if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s.#\-]+$', calle):
                    errores.append('La dirección "{direccion}" no permite caracteres especiales, solo se permiten letras, números, espacios, puntos, # y -.')
                
                # Validación de peso y altura
                peso = Decimal(str(row['Peso']).replace(',', '.'))
                altura = Decimal(str(row['Altura']).replace(',', '.'))

                if peso <= 0:
                    errores.append(f'El peso "{peso}" debe ser mayor a 0')
                
                if altura <= 0:
                    errores.append(f'La altura "{altura}" debe ser mayor a 0')

                # Verificación de duplicados
                if Paciente.objects.filter(rut=rut).exists():
                    errores.append(f'El RUT "{rut}" ya está registrado')
                
                # Si no hay errores, se guarda el paciente
                if not errores:
                    paciente = Paciente(
                        rut=rut,
                        first_name=first_name,
                        last_name=last_name,
                        fecha_nacimiento=fecha_nacimiento,
                        sexo=sexo,
                        telefono=telefono,
                        email=email,
                        contacto_emergencia=contacto_emergencia,
                        telefono_emergencia=telefono_emergencia,
                        patologia=patologia,
                        descripcion_patologia=descripcion_patologia,
                        medicamentos=medicamentos,
                        alergias=alergias,
                        actividad_fisica=actividad_fisica,
                        peso=peso,
                        altura=altura,
                        region=Region.objects.get(id=row['Region']) if not pd.isna(row['Region']) else None,
                        provincia=Provincia.objects.get(id=row['Provincia']) if not pd.isna(row['Provincia']) else None,
                        comuna=Comuna.objects.get(id=row['Comuna']) if not pd.isna(row['Comuna']) else None,
                        calle=calle
                    )
                    paciente.save()
                    registros_subidos += 1
                else:
                    # Si hay errores, no se guarda el paciente y se acumulan los mensajes de error
                    registros_no_subidos += 1
                    registros_no_validos.extend(errores)

            except Exception as e:
                registros_no_subidos += 1
                registros_no_validos.append(f'Error en la fila {fila}: {str(e)}')

        messages.success(request, f'Carga masiva finalizada. Registros subidos: {registros_subidos}. Registros no subidos: {registros_no_subidos}')
        if registros_no_validos:
            for mensaje in registros_no_validos:
                messages.error(request, mensaje)

        return redirect('listar_pacientes_activos')
    
    else:
        messages.error(request, 'No se subió ningún archivo')
        return redirect('listar_pacientes_activos')


##################################################      ADMIN RECEPCIONISTAS      ########################################################

@role_required('Administrador')
def listar_recepcionistas_activos(request):
    query = request.GET.get('search')
    order_by = request.GET.get('order_by', 'user__first_name')
    recepcionistas_list = Recepcionista.objects.filter(user__is_active=True)

    if query:
        recepcionistas_list = recepcionistas_list.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__profile__rut__icontains=query)  # Asumiendo que 'rut' está en el perfil
        )

    if order_by:
        recepcionistas_list = recepcionistas_list.order_by(order_by)
    
    paginator = Paginator(recepcionistas_list, 5)
    page_number = request.GET.get('page')
    recepcionistas = paginator.get_page(page_number)

    return render(request, 'admin_recepcionistas.html', {
        'recepcionistas': recepcionistas,
        'estado': 'activos',
        'query': query,  # Para mantener el valor en el HTML
        'order_by': order_by,  # Para saber el orden actual en el HTML
        'modulo_recepcionistas': True,
        })

@role_required('Administrador')
def listar_recepcionistas_inactivos(request):
    query = request.GET.get('search')
    order_by = request.GET.get('order_by', 'user__first_name')
    recepcionistas_list = Recepcionista.objects.filter(user__is_active=False)

    if query:
        recepcionistas_list = recepcionistas_list.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__profile__rut__icontains=query)  # Asumiendo que 'rut' está en el perfil
        )

    if order_by:
        recepcionistas_list = recepcionistas_list.order_by(order_by)
    
    paginator = Paginator(recepcionistas_list, 5)
    page_number = request.GET.get('page')
    recepcionistas = paginator.get_page(page_number)

    return render(request, 'admin_recepcionistas.html', {
        'recepcionistas': recepcionistas,
        'estado': 'inactivos',
        'query': query,  # Para mantener el valor en el HTML
        'order_by': order_by,  # Para saber el orden actual en el HTML
        'modulo_recepcionistas': True,
        })

@role_required('Administrador')
def cambiar_estado_inactivo_recepcionista(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recepcionistas_ids = data.get('recepcionistas_ids', [])
        
        # Obtener el queryset de los recepcionistas antes de actualizar su estado
        recepcionistas = Recepcionista.objects.filter(id__in=recepcionistas_ids)

        # Cambiar el estado de los recepcionistas a inactivo
        for recepcionista in recepcionistas:
            recepcionista.user.is_active = False
            recepcionista.user.save()
        
        return JsonResponse({
            'status': 'success',
            'recepcionistas_afectados': [recepcionista.id for recepcionista in recepcionistas]
        })

@role_required('Administrador')
def restaurar_recepcionista(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recepcionistas_ids = data.get('recepcionistas_ids', [])
        
        # Obtener el queryset de los recepcionistas a restaurar
        recepcionistas = Recepcionista.objects.filter(id__in=recepcionistas_ids)
        
        # Restaurar el estado de los recepcionistas a activo
        for recepcionista in recepcionistas:
            recepcionista.user.is_active = True
            recepcionista.user.save()
        
        return JsonResponse({
            'status': 'success',
            'recepcionistas_restaurados': [recepcionista.id for recepcionista in recepcionistas]
        })

@role_required('Administrador')
def agregar_terapeuta(request):

    success = False # Variable para indicar que el terapeuta no fue creado exitosamente

    if request.method == 'POST':
        terapeuta_form = CrearTerapeutaForm(request.POST)
        horario_formset = HorarioFormSet(request.POST)

        if terapeuta_form.is_valid() and horario_formset.is_valid():
            with transaction.atomic(): # Para que si algo falla, no se guarde nada, asegura que todas las operaciones se realicen correctamente
                terapeuta = terapeuta_form.save()
                horario_formset.instance = terapeuta # Asignamos el terapeuta a los horarios
                horario_formset.save()
            
            success = True # Variable para indicar que el terapeuta fue creado exitosamente
            return render(request, 'agregar_terapeuta.html', {
                'success': success,
                'terapeuta_form': CrearTerapeutaForm(), # Creamos un nuevo formulario vacío
                'horario_formset': HorarioFormSet(queryset=Horario.objects.none()),
                'modulo_terapeutas': True,
            })
        
    else:
        terapeuta_form = CrearTerapeutaForm()
        horario_formset = HorarioFormSet(queryset=Horario.objects.none()) # Creamos un formset vacío, para que no se prellene con datos
    
    return render(request, 'agregar_terapeuta.html', {
        'terapeuta_form': terapeuta_form,
        'horario_formset': horario_formset,
        'success': success, # Variable para indicar que el terapeuta no fue creado exitosamente
        'modulo_terapeutas': True,
    })

#### CARGA DE DATOS DE REGIONES, PROVINCIAS Y COMUNAS ####
def provincias_api(request):
    region_id = request.GET.get("region")
    if region_id:
        provincias = Provincia.objects.filter(region_id=region_id).values("id", "nombre")
        return JsonResponse(list(provincias), safe=False)
    else:
        return JsonResponse([], safe=False)
    
def comunas_api(request):
    provincia_id = request.GET.get("provincia")
    if provincia_id:
        comunas = Comuna.objects.filter(provincia_id=provincia_id).values("id", "nombre")
        return JsonResponse(list(comunas), safe=False)
    else:
        return JsonResponse([], safe=False)
    
@role_required('Administrador')
def mostrar_paciente_administrador(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    edad = paciente.calcular_edad()
    imc = paciente.calcular_imc()

    try:
        cita = Cita.objects.get(paciente_id=paciente_id)
    except Cita.DoesNotExist:
        cita = None  # Asigna None si no existe la cita

    return render(request, 'mostrar_paciente_administrador.html', {
        'paciente': paciente,
        'edad': edad,
        'imc': imc,
        'cita': cita,  # Envía la cita o None si no existe
        'modulo_pacientes': True,
    })
    
@role_required('Administrador')
def mostrar_recepcionista_administrador(request, recepcionista_id):
    recepcionista = Recepcionista.objects.get(id=recepcionista_id)
    return render(request, 'mostrar_recepcionista_administrador.html', {'recepcionista': recepcionista, 'modulo_recepcionistas': True})

@role_required('Administrador')
def mostrar_terapeuta_administrador(request, terapeuta_id):
    terapeuta = Terapeuta.objects.get(id=terapeuta_id)

    print(terapeuta)
    return render(request, 'mostrar_terapeuta_administrador.html', {'terapeuta': terapeuta, 'modulo_terapeutas': True})
    
@role_required('Administrador')
def listado_terapeutas(request, paciente_id):
    paciente = Paciente.objects.get(id=paciente_id)
    terapeuta = Terapeuta.objects.all()
    return render(request, 'listado_terapeutas.html', {'terapeuta': terapeuta, 'paciente': paciente, 'modulo_pacientes': True})

@role_required('Administrador')
def calendar_asignar_paciente_administrador(request, paciente_id, terapeuta_id):
    terapeuta = Terapeuta.objects.get(id=terapeuta_id)
    paciente = Paciente.objects.get(id=paciente_id)
    cita = Cita.objects.all()
    horario_terapeuta = {
        'lunes': {'inicio': 8, 'fin': 13},
        'martes': {'inicio': 8, 'fin': 13},
        'miercoles': {'inicio': 8, 'fin': 13},
        'jueves': {'inicio': 8, 'fin': 13},
        'viernes': {'inicio': 8, 'fin': 13},
        'sabado': None,
        'domingo': None,
    }
    return render(request, 'calendar_asignar_paciente_administrador.html', {'horario_terapeuta': horario_terapeuta, 'cita': cita,
                                                              'paciente':paciente, 'terapeuta':terapeuta, 'modulo_pacientes': True})
@role_required('Administrador')
def agendar_cita_administrador(request, paciente_id, terapeuta_id):
    terapeuta_instance = get_object_or_404(Terapeuta, id=terapeuta_id)
    paciente_instance = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        titulo = request.POST['titulo']
        fecha = request.POST['fecha']
        hora = request.POST['hora']
        sala = request.POST['sala']
        detalle = request.POST['detalle']

        # Obtener todas las citas existentes del paciente con ese terapeuta
        citas_existentes = Cita.objects.filter(paciente=paciente_instance)

        # Eliminar todas las citas anteriores (si existen)
        citas_existentes.delete()

        # Crear una nueva cita
        cita = Cita(
            terapeuta=terapeuta_instance,
            paciente=paciente_instance,
            titulo=titulo,
            fecha=fecha,
            hora=hora,
            sala=sala,
            detalle=detalle
        )
        cita.save()

        mensaje = "Cita creada y citas anteriores eliminadas exitosamente."

        return redirect('mostrar_paciente_administrador', paciente_instance.id)

    return render(request, 'mostrar_paciente_administrador.html', {'paciente': paciente_instance, 'modulo_pacientes': True})

@role_required('Administrador')
def editar_datos_paciente_admin(request, paciente_id, terapeuta=None):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Obtener la lista de terapeutas
    terapeutas = Terapeuta.objects.all()
    
    if request.method == 'POST':
        form = EditarPacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos guardados exitosamente.')
            # Redirigir a la misma página con un parámetro de éxito en la URL
            return redirect('editar_datos_paciente_admin', paciente_id=paciente_id)


    
    else:
        # Pasar la instancia del paciente para rellenar los campos, incluyendo fecha_nacimiento
        form = EditarPacienteForm(instance=paciente)

    # Renderizar la plantilla
    return render(request, 'editar_datos_paciente_admin.html', {
        'paciente': paciente,
        'terapeutas': terapeutas,
        'terapeuta_asignado': paciente.terapeuta.id if paciente.terapeuta else None,
        'paciente_form': form,
        'modulo_pacientes': True,
    })

@role_required('Administrador')
def redirigir_asignar_cita(request, terapeuta_id, paciente_id):
    return redirect('calendar_asignar_paciente_administrador', terapeuta_id=terapeuta_id, paciente_id=paciente_id)