from django.shortcuts import render, get_object_or_404, redirect
from terapeuta.models import Terapeuta, Paciente, Cita
from autenticacion.models import Profile
from autenticacion.decorators import role_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone


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

@role_required('Recepcionista')
def recepcionista_pacientes_activos(request):
    paciente = Paciente.objects.all()
    return render(request, 'recepcionista_pacientes_activos.html', {'paciente': paciente})

@role_required('Recepcionista')
def agregar_paciente(request):
    return render(request, 'agregar_paciente.html')

def asignar_terapeuta(request, id):
    paciente = Paciente.objects.get(id=id)
    terapeuta = Terapeuta.objects.all()
    return render(request, 'asignar_terapeuta.html', {'terapeuta': terapeuta, 'paciente': paciente})


    
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

def calendar_asignar_paciente(request, id):
    terapeuta = get_object_or_404(Terapeuta, id=id)
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
    return render(request, 'calendar_asignar_paciente.html', {'horario_terapeuta': horario_terapeuta, 'cita': cita})


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
        dispositivo_ortesis = request.POST.get('dispositivo_ortesis', None)
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
            dispositivo_ortesis=dispositivo_ortesis,
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

def mostrar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    return render(request, 'mostrar_paciente.html', {'paciente': paciente})

