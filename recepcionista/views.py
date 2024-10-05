import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from terapeuta.models import Terapeuta, Paciente, Cita
from autenticacion.models import Profile
from autenticacion.decorators import role_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .forms import CrearPacienteForm, EditarPacienteForm
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.contrib import messages

@role_required('Recepcionista')
def recepcionista_terapeutas_activos(request):
    '''query = request.GET.get('q', '')
    if query:
        terapeuta = Terapeuta.objects.filter(
            estado='activo',
            nombre__icontains=query
        ) | Terapeuta.objects.filter(
            estado='activo',
            rut__icontains=query
        )
    else:
    '''
    terapeuta = Terapeuta.objects.all()

    return render(request, 'recepcionista_terapeutas_activos.html', {'terapeuta': terapeuta})


def calcular_edad(fecha_nacimiento):
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

###################################     PACIENTES     ###################################

@role_required('Recepcionista')
def recepcionista_pacientes_activos(request):
    query = request.GET.get('search')
    pacientes_list = Paciente.objects.filter(is_active=True)

    # Si hay un parámetro de búsqueda, filtrar los pacientes
    if query:
        pacientes_list = pacientes_list.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(rut__icontains=query) |
            Q(patologia__icontains=query)
        )

    # Calcular la edad de cada paciente
    for paciente in pacientes_list:
        paciente.edad = calcular_edad(paciente.fecha_nacimiento)

    total_pacientes = pacientes_list.count()

    paginator = Paginator(pacientes_list, 15)
    page_number = request.GET.get('page') 
    pacientes = paginator.get_page(page_number)

    # Renderizar el template con los pacientes y la información de paginación
    return render(request, 'recepcionista_pacientes.html', {'pacientes': pacientes, 'total_pacientes': total_pacientes, 'estado': 'activos'})

@role_required('Recepcionista')
def recepcionista_pacientes_inactivos(request):
    query = request.GET.get('search')
    pacientes_list = Paciente.objects.filter(is_active=False)

    # Si hay un parámetro de búsqueda, filtrar los pacientes
    if query:
        pacientes_list = pacientes_list.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(rut__icontains=query) |
            Q(patologia__icontains=query)
        )

    # Calcular la edad de cada paciente
    for paciente in pacientes_list:
        paciente.edad = calcular_edad(paciente.fecha_nacimiento)

    total_pacientes = pacientes_list.count()

    paginator = Paginator(pacientes_list, 15)
    page_number = request.GET.get('page') 
    pacientes = paginator.get_page(page_number)

    # Renderizar el template con los pacientes y la información de paginación
    return render(request, 'recepcionista_pacientes.html', {'pacientes': pacientes, 'total_pacientes': total_pacientes, 'estado': 'inactivos'})


@role_required('Recepcionista')
def recepcionista_cambiar_estado_inactivo(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pacientes_ids = data.get('pacientes_ids', [])
        Paciente.objects.filter(id__in=pacientes_ids).update(is_active=False)
        return JsonResponse({'status': 'success'})

@role_required('Recepcionista')
def recepcionista_restaurar_paciente(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pacientes_ids = data.get('pacientes_ids', [])
        Paciente.objects.filter(id__in=pacientes_ids).update(is_active=True)
        return JsonResponse({'status': 'success'})


@role_required('Recepcionista')
def agregar_paciente(request):
    if request.method == 'POST':
        paciente_form = CrearPacienteForm(request.POST)
        
        if paciente_form.is_valid():
            paciente = paciente_form.save()
            paciente_id = paciente.id
            return redirect('mostrar_paciente_sin_terapeuta', paciente_id = paciente_id)
    else:
        paciente_form = CrearPacienteForm()
    
    return render(request, 'agregar_paciente.html', {'paciente_form': paciente_form})

@role_required('Recepcionista')
def elegir_terapeuta(request, id):
    paciente = Paciente.objects.get(id=id)
    terapeuta = Terapeuta.objects.all()
    return render(request, 'elegir_terapeuta.html', {'terapeuta': terapeuta, 'paciente': paciente})

@role_required('Recepcionista')
def asignar_terapeuta(request, terapeuta_id, paciente_id):
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
    return render(request, 'mostrar_paciente_recepcionista.html', {'paciente': paciente})


@role_required('Recepcionista')
def listar_terapeutas_activos(request):
    query = request.GET.get('q', '')
    orden = request.GET.get('orden', 'user__first_name')  # Valor por defecto para ordenación
    valid_order_fields = ['user__first_name', 'user__last_name', 'user__profile__rut', 'especialidad', 'fecha_contratacion']
    if orden not in valid_order_fields:
        orden = 'user__first_name'  # Restablecer a un valor por defecto si no es válido

    # Filtrado de terapeutas activos
    if query:
        terapeutas = Terapeuta.objects.filter(
            Q(user__first_name__icontains=query) | 
            Q(user__last_name__icontains=query) | 
            Q(user__profile__rut__icontains=query),
            user__is_active=True  # Filtrar por usuarios activos
        ).order_by(orden)  # Aplicar ordenación
    else:
        terapeutas = Terapeuta.objects.filter(user__is_active=True).order_by(orden)  # Aplicar ordenación

    # Paginación
    paginator = Paginator(terapeutas, 5)  # 5 terapeutas por página
    page_number = request.GET.get('page')  # Obtener el número de página de la URL
    page_obj = paginator.get_page(page_number)  # Obtener la página correspondiente

    return render(request, 'terapeutas.html', {'terapeutas': page_obj})

@role_required('Recepcionista')
def calendar_asignar_paciente(request, paciente_id, terapeuta_id):
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
    return render(request, 'calendar_asignar_paciente.html', {'horario_terapeuta': horario_terapeuta, 'cita': cita,
                                                              'paciente':paciente, 'terapeuta':terapeuta})

@role_required('Recepcionista')
def agendar_cita_recepcionista(request, paciente_id, terapeuta_id):
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

        return redirect('mostrar_paciente_recepcionista', paciente_instance.id)

    return render(request, 'mostrar_paciente_recepcionista.html', {'paciente': paciente_instance})


    
def formulario_agregar_paciente(request):
    if request.method == 'POST':
        # Campos obligatorios
        nombres = request.POST['nombres']
        apellidos = request.POST['apellidos']
        rut = request.POST['rut']
        fecha_nacimiento = request.POST['fecha_nacimiento']
        sexo = request.POST['sexo']

        # Campos opcionales (pueden ser nulos)
        telefono = request.POST.get('telefono', None)
        correo = request.POST.get('correo', None)
        contacto_emergencia = request.POST.get('contacto_emergencia', None)
        telefono_emergencia = request.POST.get('telefono_emergencia', None)
        historial_medico = request.POST.get('historial_medico', None)
        medicamentos = request.POST.get('medicamentos', None)
        patologia = request.POST.get('patologia', None)
        alergias = request.POST.get('alergias', None)
        progreso = request.POST.get('progreso', None)
        actividad_fisica = request.POST.get('actividad_fisica', None)
        peso = request.POST.get('peso', None)
        altura = request.POST.get('altura', None)
        imc = request.POST.get('imc', None)
        motivo_desvinculacion = request.POST.get('motivo_desvinculacion', None)

        # Obtener la fecha y hora actuales
        date_joined = timezone.now()

        # Crear el objeto paciente
        paciente = Paciente(
            first_name=nombres,
            last_name=apellidos,
            rut=rut,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            telefono=telefono,
            email=correo,
            contacto_emergencia=contacto_emergencia,
            telefono_emergencia=telefono_emergencia,
            historial_medico=historial_medico,
            medicamentos=medicamentos,
            patologia=patologia,
            alergias=alergias,
            progreso=progreso,
            actividad_fisica=actividad_fisica,
            peso=peso,
            altura=altura,
            imc=imc,
            motivo_desvinculacion=motivo_desvinculacion,
            date_joined=date_joined  # Fecha de registro
        )
        paciente.save()

        return redirect('recepcionista_pacientes_activos')

    return render(request, 'agregar_paciente.html')

def mostrar_paciente_sin_terapeuta(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    edad = paciente.calcular_edad()
    imc = paciente.calcular_imc()
    cita = Cita.objects.filter(paciente_id=paciente_id).last()
    return render(request, 'mostrar_paciente_recepcionista.html', {'paciente': paciente, 'edad': edad, 'cita': cita, 'imc': imc})


def mostrar_paciente_con_terapeuta(request, paciente_id, terapeuta_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    terapeuta = Terapeuta.objects.get(id=terapeuta_id)
    edad = paciente.calcular_edad()
    imc = paciente.calcular_imc()
    cita = Cita.objects.filter(paciente_id=paciente_id).last()
    return render(request, 'mostrar_paciente_recepcionista.html', {'paciente': paciente, 'edad': edad, 'cita': cita, 'imc': imc, 'terapeuta':terapeuta})

@role_required('Recepcionista')
def mostrar_paciente_recepcionista(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    edad = paciente.calcular_edad()
    imc = paciente.calcular_imc()

    try:
        cita = Cita.objects.get(paciente_id=paciente_id)
    except Cita.DoesNotExist:
        cita = None  # Asigna None si no existe la cita

    return render(request, 'mostrar_paciente_recepcionista.html', {
        'paciente': paciente,
        'edad': edad,
        'imc': imc,
        'cita': cita  # Envía la cita o None si no existe
    })

@role_required('Recepcionista')
def editar_datos_paciente_recepcionista(request, paciente_id, terapeuta=None):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Obtener la lista de terapeutas
    terapeutas = Terapeuta.objects.all()

    # Obtener la última cita del paciente
    ultima_cita = Cita.objects.filter(paciente=paciente).order_by('-fecha', '-hora').first()
    fecha_cita = ultima_cita.fecha if ultima_cita else None
    
    if request.method == 'POST':
        form = EditarPacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos guardados exitosamente.')
            # Redirigir a la misma página con un parámetro de éxito en la URL
            return redirect('editar_datos_paciente_recepcionista', paciente_id=paciente_id)


    
    else:
        # Pasar la instancia del paciente para rellenar los campos, incluyendo fecha_nacimiento
        form = EditarPacienteForm(instance=paciente)

    # Renderizar la plantilla
    return render(request, 'editar_datos_paciente_recepcionista.html', {
        'paciente': paciente,
        'terapeutas': terapeutas,
        'terapeuta_asignado': paciente.terapeuta.id if paciente.terapeuta else None,
        'fecha_cita': fecha_cita,
        'paciente_form': form
    })
