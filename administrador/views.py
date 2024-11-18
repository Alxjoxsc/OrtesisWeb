import json
import re
import csv
from django.conf import settings
import pandas as pd
from decimal import Decimal
from datetime import date, datetime
from itertools import cycle
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from autenticacion.decorators import role_required
from django.http import HttpResponse, JsonResponse
from .forms import CrearTerapeutaForm, HorarioFormSet, CrearPacienteForm, EditarPacienteForm, CrearRecepcionistaForm, EditarTerapeutaForm
from autenticacion.models import Comuna, Region
from terapeuta.models import Paciente, Terapeuta, Cita, Horario
from recepcionista.models import Recepcionista
from autenticacion.models import Profile
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.conf import settings
import string
import random
from django.contrib.auth.hashers import make_password

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
    
#                   CARGA MASIVA TERAPEUTAS                 #
def archivo_csv_ejemplo_terapeutas(request):
    response =  HttpResponse(content_type='text/ charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="ejemplo_carga_masiva_terapeutas.csv"'
    response.write('\ufeff'.encode('utf8'))  # Escribe el BOM para UTF-8

    writer = csv.writer(response)

    writer.writerow([
        'Rut', 'Nombre', 'Apellido', 'Fecha Nacimiento', 'Sexo', 'Telefono', 
        'Email', 'Dirección', 'Region', 'Comuna', 'Especialidad', 'Disponibilidad',
        'Fecha Contrato', 'Titulo', 'Experiencia', 'Correo de contacto'
    ])
    
    writer.writerow([
        '18.424.681-3', 'Ignacio', 'Núñez', '1990-01-01', 'Masculino', '9 1234 5678', 
        'correo@example.com', 'Los Alamos 1234', '1', '1', 'Lesión muscular', 'Disponible',
        '2024-01-14', 'Terapia ocupacional', '5', 'correocontacto@example.com'
    ])
    
    return response

def carga_masiva_terapeutas(request):
    registros_subidos = 0
    registros_no_subidos = 0
    registros_no_validos = []
    COLUMNAS_ESPERADAS = 16

    if request.method == 'POST':
        if 'archivo_csv' not in request.FILES:
            messages.error(request, 'No se subió ningún archivo.')
            return redirect('listar_terapeutas_activos')
        
        archivo_csv = request.FILES['archivo_csv']

        try:
            archivo_csv.seek(0)  # Reinicia el puntero del archivo
            contenido = archivo_csv.read()

            if contenido is None:
                messages.error(request, 'Error: el archivo no contiene datos.')
                return redirect('listar_terapeutas_activos')

            # Intentamos decodificar
            try:
                contenido_decodificado = contenido.decode('utf-8')

            except UnicodeDecodeError:
                messages.error(request, 'Error al decodificar el archivo. Asegúrate de que esté en formato UTF-8.')
                return redirect('listar_terapeutas_activos')
            
            except Exception as e:
                messages.error(request, f'Error desconocido al decodificar: {e}')
                return redirect('listar_terapeutas_activos')

            if not contenido_decodificado:
                messages.error(request, 'Error: el archivo está vacío después de la decodificación.')
                return redirect('listar_terapeutas_activos')

            # Cargamos el archivo CSV
            try:
                reader = csv.reader(contenido_decodificado.splitlines())
                
                # Lee la primera fila del archivo (encabezado)
                encabezado = next(reader)
                encabezado = [col.lstrip('\ufeff') for col in encabezado]  # Elimina el BOM de todas las columnas

            except Exception as e:
                messages.error(request, f'Error al procesar el archivo CSV: {e}')
                return redirect('listar_terapeutas_activos')
            
            if len(encabezado) != COLUMNAS_ESPERADAS:
                messages.error(request, f'El archivo debe tener exactamente {COLUMNAS_ESPERADAS} columnas. '
                                        f'Se encontraron {len(encabezado)} columnas.')
                return redirect('listar_terapeutas_activos')

            fila_numero = 1  # Variable para contar las filas (empezamos desde 1)
            for fila in reader:  # Itera sobre las filas del archivo
                fila_numero += 1

                if len(fila) != COLUMNAS_ESPERADAS:
                    registros_no_subidos += 1
                    registros_no_validos.append(f'Error en la fila {fila_numero}: La fila tiene {len(fila)} columnas, se esperaban {COLUMNAS_ESPERADAS}')
                    continue

                # Convertir la fila en un diccionario y pasarla a pandas para validaciones
                data_row = dict(zip(encabezado, fila))  # Crea un diccionario con los encabezados y los valores de la fila
                errores = validar_datos_fila_terapeutas(data_row, fila_numero)

                if not errores:
                    guardar_terapeuta(data_row)
                    registros_subidos += 1
                else:
                    registros_no_subidos += 1
                    registros_no_validos.extend(errores)

        except Exception as e:
            messages.error(request, f'Error al leer el archivo: {str(e)}')
            return redirect('listar_terapeutas_activos')
    
        messages.success(request, f'Carga masiva finalizada. Registros subidos: {registros_subidos}. Registros no subidos: {registros_no_subidos}')
        if registros_no_validos:
            for mensaje in registros_no_validos:
                messages.error(request, mensaje)
        
        return redirect('listar_terapeutas_activos')
    
    else:
        messages.error(request, 'No se subió ningún archivo')
        return redirect('listar_terapeutas_activos')
    
def validar_datos_fila_terapeutas(row, fila_numero):
    errores = []
    rut = row.get('Rut')
    first_name = row.get('Nombre')
    last_name = row.get('Apellido')
    fecha_nacimiento = row.get('Fecha Nacimiento')
    sexo = row.get('Sexo').capitalize()
    telefono = row.get('Telefono')
    email = row.get('Email')
    direccion = row.get('Dirección')
    region = row.get('Region')
    comuna = row.get('Comuna')
    especialidad = row.get('Especialidad')
    disponibilidad = row.get('Disponibilidad')
    fecha_contrato = row.get('Fecha Contrato')
    titulo = row.get('Titulo')
    experiencia = int(row.get('Experiencia'))
    correo_contacto = row.get('Correo de contacto')

    # Validación de Rut
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
        errores.append(f'Fila {fila_numero}: Fila {fila_numero}: El dígito verificador del RUT "{rut}" no es válido')

        # Validación para el primer nombre, permite hasta 3 nombres con letras y caracteres especiales
    if not re.match(r'^[a-zA-Z\u00C0-\u017F]+( [a-zA-Z\u00C0-\u017F]+){0,2}$', first_name):
        errores.append(f'Fila {fila_numero}: El nombre "{first_name}" solo puede contener letras y hasta 3 nombres separados por espacios')
    
    # Validación para el apellido, permite hasta 2 apellidos con letras y caracteres especiales
    if not re.match(r'^[a-zA-Z\u00C0-\u017F]+( [a-zA-Z\u00C0-\u017F]+)?$', last_name):
        errores.append(f'Fila {fila_numero}: El apellido "{last_name}" solo puede contener letras y hasta 2 apellidos separados por un espacio')
    
    # Validación de correo electrónico
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        errores.append(f'Fila {fila_numero}: El correo "{email}" no es válido')
    
    # Validación de teléfono
    if not re.match(r'^\d{1} \d{4} \d{4}$', telefono):
        errores.append(f'Fila {fila_numero}: El teléfono "{telefono}" debe tener el formato: 9 1234 5678')

    # Validación de fecha de nacimiento
    try:
        fecha_valida_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
        if fecha_valida_nacimiento.date() >= date.today():
            errores.append(f'Fila {fila_numero}: La fecha de nacimiento "{fecha_nacimiento}" debe ser anterior a la fecha actual')
    except ValueError:
        errores.append(f'Fila {fila_numero}: La fecha de nacimiento "{fecha_nacimiento}" debe tener el formato YYYY-MM-DD y ser una fecha válida.')
    
    # Validación de sexo
    if sexo not in ['Masculino', 'Femenino']:
        errores.append(f'Fila {fila_numero}: El sexo "{sexo}" debe ser "Masculino" o "Femenino"')
    
    #Validación de dirección
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s.#\-]+$', direccion):
        errores.append(f'Fila {fila_numero}: La dirección "{direccion}" no permite caracteres especiales, solo se permiten letras, números, espacios, puntos, # y -.')

    #Validación de especialidad
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', especialidad):
        errores.append(f'Fila {fila_numero}: La especialidad "{especialidad}" solo puede contener letras y espacios')
    
    #Validación de disponibilidad
    if disponibilidad not in ['Disponible', 'Medianamente disponible', 'No disponible']:
        errores.append(f'Fila {fila_numero}: La disponibilidad "{disponibilidad}" debe ser "Disponible", "Medianamente disponible" o "No disponible"')

    # Validación de fecha de contrato
    try:
        fecha_valida_contrato = datetime.strptime(fecha_contrato, '%Y-%m-%d')
        if fecha_valida_contrato.date() >= date.today():
            errores.append(f'Fila {fila_numero}: La fecha de contrato "{fecha_contrato}" debe ser anterior a la fecha actual')
    except ValueError:
        errores.append(f'Fila {fila_numero}: La fecha de contrato "{fecha_contrato}" debe tener el formato YYYY-MM-DD y ser una fecha válida.')
    
    #Validación de título
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', titulo):
        errores.append(f'Fila {fila_numero}: El título "{titulo}" solo puede contener letras y espacios')
    
    #Validación de experiencia
    if experiencia < 0:
        errores.append(f'Fila {fila_numero}: La experiencia "{experiencia}" debe ser un número positivo')
    
    #Validación de correo de contacto
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', correo_contacto):
        errores.append(f'Fila {fila_numero}: El correo de contacto "{correo_contacto}" no es válido')

    # Verificación de duplicados
    if Profile.objects.filter(rut=rut).exists():
        errores.append(f'Fila {fila_numero}: El RUT "{rut}" ya está registrado')
    
    return errores


def guardar_terapeuta(row):
    user = User(
        username=row.get('Rut', ''),
        first_name=row.get('Nombre', ''),
        last_name=row.get('Apellido', ''),
        email=row.get('Email', ''),
        is_active=True,
        password=get_random_string(12),
    )
    user.save()

    #Agregar el usuario al grupo 'Recepcionista'
    group = Group.objects.get(name='Recepcionista')
    user.groups.add(group)

    profile = Profile(
        user=user,
        rut=row.get('Rut', ''),
        fecha_nacimiento=pd.to_datetime(row.get('Fecha Nacimiento', ''), errors='coerce'),
        telefono=row.get('Telefono', ''),
        direccion=row.get('Dirección', ''),
        region=Region.objects.get(pk=row.get('Region', '')) if row.get('Region') else None,
        comuna=Comuna.objects.get(pk=row.get('Comuna', '')) if row.get('Comuna') else None,
    )

    if row.get('Sexo', '').capitalize() == 'Masculino':
        profile.sexo = 'M'
    else:
        profile.sexo = 'F'

    profile.save()

    terapeuta = Terapeuta(
        user=user,
        especialidad=row.get('Especialidad', ''),
        disponibilidad=row.get('Disponibilidad', ''),
        fecha_contratacion=pd.to_datetime(row.get('Fecha Contrato', ''), errors='coerce'),
        titulo=row.get('Titulo', ''),
        experiencia=int(row.get('Experiencia', 0)),
        correo_contacto=row.get('Correo de contacto', ''),
    )

    terapeuta.save()

    #Enviar correo electrónico al usuario
    send_mail(
    'Bienvenido/a a la plataforma',
    f'Estimado/a {user.first_name} {user.last_name}, su cuenta ha sido creada,\n'
    f'Usuario: {user.profile.rut}\nContraseña: {user.password}\n\n'
    'Le recomendamos cambiar su contraseña al ingresar a la plataforma.',
    settings.DEFAULT_FROM_EMAIL,
    [user.email],
    fail_silently=False,
    )

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

def archivo_csv_ejemplo_pacientes(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="ejemplo_carga_masiva_paciente.csv"'
    response.write('\ufeff'.encode('utf8'))  # Escribe el BOM para UTF-8

    writer = csv.writer(response)
    
    writer.writerow([
        'Rut', 'Nombre', 'Apellido', 'Fecha Nacimiento', 'Sexo', 'Telefono', 
        'Email', 'Contacto Emergencia', 'Telefono Emergencia', 'Patologia', 
        'Descripcion Patologia', 'Medicamentos', 'Alergias', 'Actividad Fisica', 
        'Peso', 'Altura', 'Region', 'Comuna', 'Calle'
    ])
    
    writer.writerow([
        '8.895.157-3', 'Exequiel', 'Hurtado', '1990-01-01', 'Masculino', '9 1234 5678', 
        'correo@example.com', 'Contacto Emergencia', '9 8765 4321', 'Diabetes', 
        'Descripcion de la patologia', 'Insulina', 'Penicilina', 'Activo', 
        '75.5', '1.78', '1', '1', 'Calle falsa 123'
    ])
    
    return response

def carga_masiva_pacientes(request):
    registros_subidos = 0
    registros_no_subidos = 0
    registros_no_validos = []
    COLUMNAS_ESPERADAS = 19

    if request.method == 'POST':
        if 'archivo_csv' not in request.FILES:
            messages.error(request, 'No se subió ningún archivo.')
            return redirect('listar_pacientes_activos')
        
        archivo_csv = request.FILES['archivo_csv']

        try:
            archivo_csv.seek(0)  # Reinicia el puntero del archivo
            contenido = archivo_csv.read()

            if contenido is None:
                messages.error(request, 'Error: el archivo no contiene datos.')
                return redirect('listar_pacientes_activos')

            # Intentamos decodificar
            try:
                contenido_decodificado = contenido.decode('utf-8')

            except UnicodeDecodeError:
                messages.error(request, 'Error al decodificar el archivo. Asegúrate de que esté en formato UTF-8.')
                return redirect('listar_pacientes_activos')
            
            except Exception as e:
                messages.error(request, f'Error desconocido al decodificar: {e}')
                return redirect('listar_pacientes_activos')

            if not contenido_decodificado:
                messages.error(request, 'Error: el archivo está vacío después de la decodificación.')
                return redirect('listar_pacientes_activos')

            # Cargamos el archivo CSV
            try:
                reader = csv.reader(contenido_decodificado.splitlines())
                
                # Lee la primera fila del archivo (encabezado)
                encabezado = next(reader)
                encabezado = [col.lstrip('\ufeff') for col in encabezado]  # Elimina el BOM de todas las columnas

            except Exception as e:
                messages.error(request, f'Error al procesar el archivo CSV: {e}')
                return redirect('listar_pacientes_activos')
            
            if len(encabezado) != COLUMNAS_ESPERADAS:
                messages.error(request, f'El archivo debe tener exactamente {COLUMNAS_ESPERADAS} columnas. '
                                        f'Se encontraron {len(encabezado)} columnas.')
                return redirect('listar_pacientes_activos')

            fila_numero = 1  # Variable para contar las filas (empezamos desde 1)
            for fila in reader:  # Itera sobre las filas del archivo
                fila_numero += 1

                if len(fila) != COLUMNAS_ESPERADAS:
                    registros_no_subidos += 1
                    registros_no_validos.append(f'Error en la fila {fila_numero}: La fila tiene {len(fila)} columnas, se esperaban {COLUMNAS_ESPERADAS}')
                    continue

                # Convertir la fila en un diccionario y pasarla a pandas para validaciones
                data_row = dict(zip(encabezado, fila))  # Crea un diccionario con los encabezados y los valores de la fila
                errores = validar_datos_fila_pacientes(data_row, fila_numero)

                if not errores:
                    guardar_paciente(data_row)
                    registros_subidos += 1
                else:
                    registros_no_subidos += 1
                    registros_no_validos.extend(errores)

        except Exception as e:
            messages.error(request, f'Error al leer el archivo: {str(e)}')
            return redirect('listar_pacientes_activos')
        
        messages.success(request, f'Carga masiva finalizada. Registros subidos: {registros_subidos}. Registros no subidos: {registros_no_subidos}')
        if registros_no_validos:
            for mensaje in registros_no_validos:
                messages.error(request, mensaje)
        
        return redirect('listar_pacientes_activos')
    
    else:
        messages.error(request, 'No se subió ningún archivo')
        return redirect('listar_pacientes_activos')


def validar_datos_fila_pacientes(row, fila_numero):
    errores = []
    rut = row.get('Rut')
    first_name = row.get('Nombre')
    last_name = row.get('Apellido')
    fecha_nacimiento = row.get('Fecha Nacimiento')
    sexo = row.get('Sexo').capitalize()
    telefono = row.get('Telefono')
    email = row.get('Email')
    contacto_emergencia = row.get('Contacto Emergencia')
    telefono_emergencia = row.get('Telefono Emergencia')
    patologia = row.get('Patologia')
    descripcion_patologia = row.get('Descripcion Patologia')
    medicamentos = row.get('Medicamentos')
    alergias = row.get('Alergias')
    actividad_fisica = row.get('Actividad Fisica')
    peso = row.get('Peso')
    altura = row.get('Altura')
    region = row.get('Region')
    comuna = row.get('Comuna')
    calle = row.get('Calle')

    # Validación de Rut
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
        errores.append(f'Fila {fila_numero}: El dígito verificador del RUT "{rut}" no es válido')
    
    # Validación para el primer nombre, permite hasta 3 nombres con letras y caracteres especiales
    if not re.match(r'^[a-zA-Z\u00C0-\u017F]+( [a-zA-Z\u00C0-\u017F]+){0,2}$', first_name):
        errores.append(f'Fila {fila_numero}: El nombre "{first_name}" solo puede contener letras y hasta 3 nombres separados por espacios')

    # Validación para el apellido, permite hasta 2 apellidos con letras y caracteres especiales
    if not re.match(r'^[a-zA-Z\u00C0-\u017F]+( [a-zA-Z\u00C0-\u017F]+)?$', last_name):
        errores.append(f'Fila {fila_numero}: El apellido "{last_name}" solo puede contener letras y hasta 2 apellidos separados por un espacio')
    
    # Validación de correo electrónico
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        errores.append(f'Fila {fila_numero}: El correo "{email}" no es válido')
    
    # Validación de teléfono
    if not re.match(r'^\d{1} \d{4} \d{4}$', telefono):
        errores.append(f'Fila {fila_numero}: El teléfono "{telefono}" debe tener el formato: 9 1234 5678')
    
    # Validación de fecha de nacimiento
    try:
        fecha_valida_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
        if fecha_valida_nacimiento.date() >= date.today():
            errores.append(f'Fila {fila_numero}: La fecha de nacimiento "{fecha_nacimiento}" debe ser anterior a la fecha actual')
    except ValueError:
        errores.append(f'Fila {fila_numero}: La fecha de nacimiento "{fecha_nacimiento}" debe tener el formato YYYY-MM-DD y ser una fecha válida.')

    # Validación de sexo
    if sexo not in ['Masculino', 'Femenino']:
        errores.append(f'Fila {fila_numero}: El sexo "{sexo}" debe ser "Masculino" o "Femenino"')
    
    if not re.match(r'^[a-zA-Z\u00C0-\u017F]+( [a-zA-Z\u00C0-\u017F]+)?$', contacto_emergencia):
        errores.append(f'Fila {fila_numero}: El contacto de emergencia "{contacto_emergencia}" solo puede contener letras y un apellido opcional separados por un espacio')

    if not re.match(r'^\d{1} \d{4} \d{4}$', telefono_emergencia):
        errores.append(f'Fila {fila_numero}: El teléfono de emergencia "{telefono_emergencia}" debe tener el formato: 9 1234 5678')
    
    if not re.match(r'^[a-zA-Z\u00C0-\u017F ]+$', patologia):
        errores.append(f'Fila {fila_numero}: La patología "{patologia}" solo puede contener letras y espacios')

    if not re.match(r'^[a-zA-Z\u00C0-\u017F ]+$', descripcion_patologia):
        errores.append(f'Fila {fila_numero}: La descripción de la patología "{descripcion_patologia}" solo puede contener letras y espacios')

    if not re.match(r'^[a-zA-Z\u00C0-\u017F ]+$', str(medicamentos)):
        errores.append(f'Fila {fila_numero}: Los medicamentos "{medicamentos}" solo pueden contener letras y espacios')
    
    if not re.match(r'^[a-zA-Z\u00C0-\u017F ]+$', str(alergias)):
        errores.append(f'Fila {fila_numero}: Las alergias "{alergias}" solo pueden contener letras y espacios')
    
    if actividad_fisica not in ['Sedentario', 'Moderado', 'Activo']:
        errores.append(f'Fila {fila_numero}: La actividad física "{actividad_fisica}" debe ser "Sedentario", "Moderado" o "Activo"')

    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s.#\-]+$', calle):
        errores.append(f'Fila {fila_numero}: La dirección "{calle}" no permite caracteres especiales, solo se permiten letras, números, espacios, puntos, # y -.')
    
    # Validación de peso y altura
    peso = Decimal(str(row['Peso']).replace(',', '.'))
    altura = Decimal(str(row['Altura']).replace(',', '.'))

    if peso <= 0:
        errores.append(f'Fila {fila_numero}: El peso "{peso}" debe ser mayor a 0')
    
    if altura <= 0:
        errores.append(f'Fila {fila_numero}: La altura "{altura}" debe ser mayor a 0')

    # Verificación de duplicados
    if Paciente.objects.filter(rut=rut).exists():
        errores.append(f'Fila {fila_numero}: El RUT "{rut}" ya está registrado')
    
    return errores

def guardar_paciente(row):
    paciente = Paciente(
        rut=row.get('Rut', ''),
        first_name=row.get('Nombre', ''),
        last_name=row.get('Apellido', ''),
        fecha_nacimiento=pd.to_datetime(row.get('Fecha Nacimiento', ''), errors='coerce'),
        sexo=row.get('Sexo', '').capitalize(),
        telefono=row.get('Telefono', ''),
        email=row.get('Email', ''),
        contacto_emergencia=row.get('Contacto Emergencia', ''),
        telefono_emergencia=row.get('Telefono Emergencia', ''),
        patologia=row.get('Patologia', ''),
        descripcion_patologia=row.get('Descripcion Patologia', ''),
        medicamentos=row.get('Medicamentos', ''),
        alergias=row.get('Alergias', ''),
        actividad_fisica=row.get('Actividad Fisica', ''),
        peso=Decimal(str(row.get('Peso', '0')).replace(',', '.')),
        altura=Decimal(str(row.get('Altura', '0')).replace(',', '.')),
        region=Region.objects.get(pk=row.get('Region', '')) if row.get('Region') else None,
        comuna=Comuna.objects.get(pk=row.get('Comuna', '')) if row.get('Comuna') else None,
        calle=row.get('Calle', ''),
    )
    paciente.save()


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
    if request.method == 'POST':
        terapeuta_form = CrearTerapeutaForm(request.POST)
        horario_formset = HorarioFormSet(request.POST)

        if terapeuta_form.is_valid() and horario_formset.is_valid():
            with transaction.atomic():
                # Guardamos el terapeuta
                terapeuta = terapeuta_form.save()
                
                # Asignamos el terapeuta a los horarios y guardamos el formset
                horario_formset.instance = terapeuta
                horario_formset.save()
            
            # Redirigimos a la vista 'mostrar_terapeuta_administrador' con el ID del terapeuta
            return redirect('mostrar_terapeuta_administrador', terapeuta_id=terapeuta.id)
    else:
        terapeuta_form = CrearTerapeutaForm()
        horario_formset = HorarioFormSet(queryset=Horario.objects.none())  # Formset vacío
    
    return render(request, 'agregar_terapeuta.html', {
        'terapeuta_form': terapeuta_form,
        'horario_formset': horario_formset,
        'modulo_terapeutas': True,
    })

#### CARGA DE DATOS DE REGIONES Y COMUNAS ####
def comunas_api(request):
    region_id = request.GET.get("region")
    if region_id:
        # Filtrar comunas directamente por región
        comunas = Comuna.objects.filter(region_id=region_id).values("id", "nombre")
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
            # Redirigir a la misma página con un parámetro de éxito en la URL
            return JsonResponse({
                'success': True,
                'message': 'Datos guardados exitosamente.',
                'paciente_id': paciente.id
            })


    
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
        'messages': messages.get_messages(request),
    })
    
@role_required('Administrador')
def redirigir_asignar_cita(request, terapeuta_id, paciente_id):
    return redirect('calendar_asignar_paciente_administrador', terapeuta_id=terapeuta_id, paciente_id=paciente_id)

#                       CARGA MASIVA DE RECEPCIONISTAS                     #

def archivo_csv_ejemplo_recepcionistas(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="ejemplo_carga_masiva_recepcionista.csv"'
    response.write('\ufeff'.encode('utf8'))  # Escribe el BOM para UTF-8

    writer = csv.writer(response)
    
    writer.writerow([
        'Rut', 'Nombre', 'Apellido', 'Fecha Nacimiento', 'Sexo', 'Telefono', 
        'Email', 'Dirección', 'Region', 'Comuna', 'Fecha Contrato',
        'Turno', 'Experiencia', 'Formación Académica', 'Supervisor'
    ])
    
    writer.writerow([
        '16.379.436-5', 'Álvaro', 'Cepeda', '1990-01-01', 'Masculino', '9 1234 5678', 
        'correo@example.com', 'Los Alamos 1234', '1', '1', '2023-02-20', 'Mañana',
        '3', 'Profesional en Actividades Administrativas en la Relación con el Cliente', 'No'
    ])
    
    return response

def carga_masiva_recepcionistas(request):
    registros_subidos = 0
    registros_no_subidos = 0
    registros_no_validos = []
    COLUMNAS_ESPERADAS = 15

    if request.method == 'POST':
        if 'archivo_csv' not in request.FILES:
            messages.error(request, 'No se subió ningún archivo.')
            return redirect('listar_recepcionistas_activos')
        
        archivo_csv = request.FILES['archivo_csv']

        try:
            archivo_csv.seek(0)  # Reinicia el puntero del archivo
            contenido = archivo_csv.read()

            if contenido is None:
                messages.error(request, 'Error: el archivo no contiene datos.')
                return redirect('listar_recepcionistas_activos')

            # Intentamos decodificar
            try:
                contenido_decodificado = contenido.decode('utf-8')

            except UnicodeDecodeError:
                messages.error(request, 'Error al decodificar el archivo. Asegúrate de que esté en formato UTF-8.')
                return redirect('listar_recepcionistas_activos')
            
            except Exception as e:
                messages.error(request, f'Error desconocido al decodificar: {e}')
                return redirect('listar_recepcionistas_activos')

            if not contenido_decodificado:
                messages.error(request, 'Error: el archivo está vacío después de la decodificación.')
                return redirect('listar_recepcionistas_activos')

            # Cargamos el archivo CSV
            try:
                reader = csv.reader(contenido_decodificado.splitlines())
                
                # Lee la primera fila del archivo (encabezado)
                encabezado = next(reader)
                encabezado = [col.lstrip('\ufeff') for col in encabezado]  # Elimina el BOM de todas las columnas

            except Exception as e:
                messages.error(request, f'Error al procesar el archivo CSV: {e}')
                return redirect('listar_recepcionistas_activos')
            
            if len(encabezado) != COLUMNAS_ESPERADAS:
                messages.error(request, f'El archivo debe tener exactamente {COLUMNAS_ESPERADAS} columnas. '
                                        f'Se encontraron {len(encabezado)} columnas.')
                return redirect('listar_recepcionistas_activos')

            fila_numero = 1  # Variable para contar las filas (empezamos desde 1)
            for fila in reader:  # Itera sobre las filas del archivo
                fila_numero += 1

                if len(fila) != COLUMNAS_ESPERADAS:
                    registros_no_subidos += 1
                    registros_no_validos.append(f'Error en la fila {fila_numero}: La fila tiene {len(fila)} columnas, se esperaban {COLUMNAS_ESPERADAS}')
                    continue

                # Convertir la fila en un diccionario y pasarla a pandas para validaciones
                data_row = dict(zip(encabezado, fila))  # Crea un diccionario con los encabezados y los valores de la fila
                errores = validar_datos_fila_recepcionistas(data_row, fila_numero)

                if not errores:
                    guardar_recepcionista(data_row)
                    registros_subidos += 1
                else:
                    registros_no_subidos += 1
                    registros_no_validos.extend(errores)
                
        except Exception as e:
            messages.error(request, f'Error al leer el archivo: {str(e)}')
            return redirect('listar_recepcionistas_activos')
        
        messages.success(request, f'Carga masiva finalizada. Registros subidos: {registros_subidos}. Registros no subidos: {registros_no_subidos}')
        if registros_no_validos:
            for mensaje in registros_no_validos:
                messages.error(request, mensaje)
        
        return redirect('listar_recepcionistas_activos')
    
    else:
        messages.error(request, 'No se subió ningún archivo')
        return redirect('listar_recepcionistas_activos')

def validar_datos_fila_recepcionistas(row, fila_numero):
    errores = []
    rut = row.get('Rut')
    first_name = row.get('Nombre')
    last_name = row.get('Apellido')
    fecha_nacimiento = row.get('Fecha Nacimiento')
    sexo = row.get('Sexo').capitalize()
    telefono = row.get('Telefono')
    email = row.get('Email')
    direccion = row.get('Dirección')
    region = row.get('Region')
    comuna = row.get('Comuna')
    fecha_contrato = row.get('Fecha Contrato')
    turno = row.get('Turno')
    experiencia = int(row.get('Experiencia'))
    formacion_academica = row.get('Formación Académica')
    supervisor = row.get('Supervisor').capitalize()

    # Validación de Rut
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
        errores.append(f'Fila {fila_numero}: El dígito verificador del RUT "{rut}" no es válido')
    
    # Validación para el primer nombre, permite hasta 3 nombres con letras y caracteres especiales
    if not re.match(r'^[a-zA-Z\u00C0-\u017F]+( [a-zA-Z\u00C0-\u017F]+){0,2}$', first_name):
        errores.append(f'Fila {fila_numero}: El nombre "{first_name}" solo puede contener letras y hasta 3 nombres separados por espacios')
    
    # Validación para el apellido, permite hasta 2 apellidos con letras y caracteres especiales
    if not re.match(r'^[a-zA-Z\u00C0-\u017F]+( [a-zA-Z\u00C0-\u017F]+)?$', last_name):
        errores.append(f'Fila {fila_numero}: El apellido "{last_name}" solo puede contener letras y hasta 2 apellidos separados por un espacio')
    
    # Validación de correo electrónico
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        errores.append(f'Fila {fila_numero}: El correo "{email}" no es válido')
    
    # Validación de teléfono
    if not re.match(r'^\d{1} \d{4} \d{4}$', telefono):
        errores.append(f'Fila {fila_numero}: El teléfono "{telefono}" debe tener el formato: 9 1234 5678')

    # Validación de fecha de nacimiento
    try:
        fecha_valida_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
        if fecha_valida_nacimiento.date() >= date.today():
            errores.append(f'Fila {fila_numero}: La fecha de nacimiento "{fecha_nacimiento}" debe ser anterior a la fecha actual')
    except ValueError:
        errores.append(f'Fila {fila_numero}: La fecha de nacimiento "{fecha_nacimiento}" debe tener el formato YYYY-MM-DD y ser una fecha válida.')
    
    # Validación de sexo
    if sexo not in ['Masculino', 'Femenino']:
        errores.append(f'Fila {fila_numero}: El sexo "{sexo}" debe ser "Masculino" o "Femenino"')
    
    #Validación de dirección
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s.#\-]+$', direccion):
        errores.append(f'Fila {fila_numero}: La dirección "{direccion}" no permite caracteres especiales, solo se permiten letras, números, espacios, puntos, # y -.')
    
    # Validación de fecha de contrato
    try:
        fecha_valida_contrato = datetime.strptime(fecha_contrato, '%Y-%m-%d')
        if fecha_valida_contrato.date() >= date.today():
            errores.append(f'Fila {fila_numero}: La fecha de contrato "{fecha_contrato}" debe ser anterior a la fecha actual')
    except ValueError:
        errores.append(f'Fila {fila_numero}: La fecha de contrato "{fecha_contrato}" debe tener el formato YYYY-MM-DD y ser una fecha válida.')
    
    # Validación de turno
    if turno not in ['Mañana', 'Tarde', 'Noche']:
        errores.append(f'Fila {fila_numero}: El turno "{turno}" debe ser "Mañana", "Tarde" o "Noche"')
    
    # Validación de experiencia
    if experiencia < 0:
        errores.append(f'Fila {fila_numero}: La experiencia "{experiencia}" debe ser mayor o igual a 0')

    # Validación de formación académica
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', formacion_academica):
        errores.append(f'Fila {fila_numero}: La formación académica "{formacion_academica}" solo puede contener letras y caracteres especiales como tíldes.')
    
    # Validación de supervisor
    if supervisor not in ['Si', 'No']:
        errores.append(f'Fila {fila_numero}: El supervisor "{supervisor}" debe ser "Si" o "No"')
    
    # Verificación de duplicados
    if Profile.objects.filter(rut=rut).exists():
        errores.append(f'Fila {fila_numero}: El RUT "{rut}" ya está registrado')
    
    return errores

def guardar_recepcionista(row):
    user = User(
        username=row.get('Rut', ''),
        first_name=row.get('Nombre', ''),
        last_name=row.get('Apellido', ''),
        email=row.get('Email', ''),
        is_active=True,
        password=get_random_string(12),
    )
    user.save()

    #Agregar el usuario al grupo 'Recepcionista'
    group = Group.objects.get(name='Recepcionista')
    user.groups.add(group)

    profile = Profile(
        user=user,
        rut=row.get('Rut', ''),
        fecha_nacimiento=pd.to_datetime(row.get('Fecha Nacimiento', ''), errors='coerce'),
        telefono=row.get('Telefono', ''),
        direccion=row.get('Dirección', ''),
        region=Region.objects.get(pk=row.get('Region', '')) if row.get('Region') else None,
        comuna=Comuna.objects.get(pk=row.get('Comuna', '')) if row.get('Comuna') else None,
    )

    if row.get('Sexo', '').capitalize() == 'Masculino':
        profile.sexo = 'M'
    else:
        profile.sexo = 'F'

    profile.save()

    recepcionista = Recepcionista(
        user=user,
        fecha_contratacion=pd.to_datetime(row.get('Fecha Contrato', ''), errors='coerce'),
        turno=row.get('Turno', ''),
        experiencia=int(row.get('Experiencia', 0)),
        formacion_academica=row.get('Formación Académica', ''),
    )

    if row.get('Supervisor', '').capitalize() == 'Si':
        recepcionista.supervisor = True
    else:
        recepcionista.supervisor = False

    recepcionista.save()

    #Enviar correo electrónico al usuario
    send_mail(
    'Bienvenido/a a la plataforma',
    f'Estimado/a {user.first_name} {user.last_name}, su cuenta ha sido creada,\n'
    f'Usuario: {user.profile.rut}\nContraseña: {user.password}\n\n'
    'Le recomendamos cambiar su contraseña al ingresar a la plataforma.',
    settings.DEFAULT_FROM_EMAIL,
    [user.email],
    fail_silently=False,
    )
def verificar_password_admin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        password = data.get('password', '')

        user = request.user
        if user.is_authenticated and user.is_staff:
            authenticated_user = authenticate(username=user.username, password=password)
            if authenticated_user is not None:
                return JsonResponse({'valid': True})
            else:
                return JsonResponse({'valid': False})
        else:
            return JsonResponse({'valid': False})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
def actualizar_email_terapeuta(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        terapeuta_id = data.get('terapeuta_id')
        nuevo_email = data.get('nuevo_email')

        try:
            terapeuta = Terapeuta.objects.get(id=terapeuta_id)
            usuario = terapeuta.user
            old_email = usuario.email

            # Verificar que el nuevo correo no esté en uso
            if User.objects.filter(email=nuevo_email).exclude(id=usuario.id).exists():
                return JsonResponse({'status': 'error', 'message': 'El correo electrónico ya está en uso.'})

            # Actualizar el correo electrónico
            usuario.email = nuevo_email
            usuario.save()

            # Enviar notificación al correo anterior
            asunto = 'Cambio de correo electrónico'
            mensaje = f'Su correo electrónico asociado a su cuenta ha sido cambiado a {nuevo_email}. Si usted no realizó este cambio, por favor contacte al administrador.'
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [old_email],
                fail_silently=False,
            )

            return JsonResponse({'status': 'success'})
        except Terapeuta.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Terapeuta no encontrado.'})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
def actualizar_credenciales_terapeuta(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        terapeuta_id = data.get('terapeuta_id')

        try:
            terapeuta = Terapeuta.objects.get(id=terapeuta_id)
            usuario = terapeuta.user

            # Generar una nueva contraseña aleatoria
            nueva_contrasena = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            usuario.password = make_password(nueva_contrasena)
            usuario.save()

            # Enviar correo electrónico al terapeuta con la nueva contraseña
            asunto = 'Actualización de Credenciales de Acceso'
            mensaje = f'Estimado/a {usuario.first_name},\n\nSus credenciales de acceso han sido actualizadas. Su nueva contraseña es: {nueva_contrasena}\n\nPor favor, inicie sesión y cambie su contraseña por una de su preferencia.\n\nSaludos cordiales.'
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                fail_silently=False,
            )

            return JsonResponse({'status': 'success'})
        except Terapeuta.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Terapeuta no encontrado.'})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
def actualizar_email_recepcionista(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recepcionista_id = data.get('recepcionista_id')
        nuevo_email = data.get('nuevo_email')

        try:
            recepcionista = Recepcionista.objects.get(id=recepcionista_id)
            usuario = recepcionista.user
            old_email = usuario.email

            # Verificar que el nuevo correo no esté en uso
            if User.objects.filter(email=nuevo_email).exclude(id=usuario.id).exists():
                return JsonResponse({'status': 'error', 'message': 'El correo electrónico ya está en uso.'})

            # Actualizar el correo electrónico
            usuario.email = nuevo_email
            usuario.save()

            # Enviar notificación al correo anterior
            asunto = 'Cambio de correo electrónico'
            mensaje = f'Su correo electrónico asociado a su cuenta ha sido cambiado a {nuevo_email}. Si usted no realizó este cambio, por favor contacte al administrador.'
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [old_email],
                fail_silently=False,
            )

            return JsonResponse({'status': 'success'})
        except Recepcionista.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Recepcionista no encontrado.'})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def actualizar_credenciales_recepcionista(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        recepcionista_id = data.get('recepcionista_id')

        try:
            recepcionista = Recepcionista.objects.get(id=recepcionista_id)
            usuario = recepcionista.user

            # Generar una nueva contraseña aleatoria
            nueva_contrasena = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            usuario.password = make_password(nueva_contrasena)
            usuario.save()

            # Enviar correo electrónico al recepcionista con la nueva contraseña
            asunto = 'Actualización de Credenciales de Acceso'
            mensaje = f'Estimado/a {usuario.first_name},\n\nSus credenciales de acceso han sido actualizadas. Su nueva contraseña es: {nueva_contrasena}\n\nPor favor, inicie sesión y cambie su contraseña por una de su preferencia.\n\nSaludos cordiales.'
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                fail_silently=False,
            )

            return JsonResponse({'status': 'success'})
        except Recepcionista.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Recepcionista no encontrado.'})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@role_required('Administrador')
def agregar_recepcionista(request):
    if request.method == 'POST':
        recepcionista_form = CrearRecepcionistaForm(request.POST)
        if recepcionista_form.is_valid():
            with transaction.atomic():
                # Guardamos el recepcionista
                recepcionista = recepcionista_form.save()
            
            # Redirigimos a la vista 'mostrar_recepcionista_administrador' con el ID del recepcionista
            return redirect('mostrar_recepcionista_administrador', recepcionista_id=recepcionista.id)
    else:
        recepcionista_form = CrearRecepcionistaForm()

    return render(request, 'agregar_recepcionista_admin.html', {
        'recepcionista_form': recepcionista_form,
        'modulo_recepcionistas': True,
    })


    
@role_required('Administrador')
def editar_datos_terapeuta_admin(request, terapeuta_id):
    terapeuta = get_object_or_404(Terapeuta, id=terapeuta_id)

    if request.method == 'POST':
        form = EditarTerapeutaForm(request.POST, instance=terapeuta)

        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Datos guardados exitosamente.',
                'terapeuta_id': terapeuta.id
            })

    else:
        form = EditarTerapeutaForm(
            initial={
                'first_name': terapeuta.user.first_name,
                'last_name': terapeuta.user.last_name,
                'rut': terapeuta.user.profile.rut,
                'telefono': terapeuta.user.profile.telefono,
                'fecha_nacimiento': terapeuta.user.profile.fecha_nacimiento,
                'direccion': terapeuta.user.profile.direccion,
                'sexo': terapeuta.user.profile.sexo,
                'comuna': terapeuta.user.profile.comuna,
                'region': terapeuta.user.profile.region,
                'especialidad': terapeuta.especialidad,
                'fecha_ingreso': terapeuta.fecha_ingreso,
                'disponibilidad': terapeuta.disponibilidad,
                'fecha_contratacion': terapeuta.fecha_contratacion,
                'titulo': terapeuta.titulo,
                'experiencia': terapeuta.experiencia,
                'presentacion': terapeuta.presentacion,
                'correo_contacto': terapeuta.correo_contacto,
            }
        )

    return render(request, 'editar_datos_terapeuta_admin.html', {
        'terapeuta': terapeuta,
        'terapeuta_form': form,
        'modulo_terapeutas': True,
        'messages': messages.get_messages(request),
    })


