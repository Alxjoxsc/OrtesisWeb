import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from autenticacion.decorators import role_required
from .forms import CrearTerapeutaForm, HorarioFormSet, CrearPacienteForm, EditarPacienteForm, CrearRecepcionistaForm
from autenticacion.models import Provincia, Comuna
from django.http import JsonResponse
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

@role_required('Administrador')
def agregar_recepcionista(request):

    success = False # Variable para indicar que el recepcionista no fue creado exitosamente

    if request.method == 'POST':
        recepcionista_form = CrearRecepcionistaForm(request.POST)

        if recepcionista_form.is_valid():
            with transaction.atomic(): # Para que si algo falla, no se guarde nada, asegura que todas las operaciones se realicen correctamente
                recepcionista = recepcionista_form.save()
            
            success = True # Variable para indicar que el recepcionista fue creado exitosamente
            return render(request, 'agregar_recepcionista.html', {
                'success': success,
                'recepcionista_form': CrearRecepcionistaForm(), # Creamos un nuevo formulario vacío
                'modulo_recepcionistas': True,
            })
        
    else:
        recepcionista_form = CrearRecepcionistaForm()
    
    return render(request, 'agregar_recepcionista.html', {
        'recepcionista_form': recepcionista_form,
        'success': success, # Variable para indicar que el terapeuta no fue creado exitosamente
        'modulo_recepcionistas': True,
    })