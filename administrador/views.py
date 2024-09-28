import json
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from autenticacion.decorators import role_required
from .forms import CrearTerapeutaForm, HorarioFormSet
from autenticacion.models import Provincia, Comuna
from django.http import JsonResponse
from terapeuta.models import Paciente, Terapeuta, Cita

# Create your views here.
@role_required('Administrador')
def gestion_terapeutas(request):
    return render(request, 'gestion_terapeutas.html')

def base_admin_view(request):
    return render(request, 'base_admin.html')
################### ADMIN PACIENTES ##################
def admin_pacientes(request):
    pacientes = Paciente.objects.all() 
    return render(request, 'admin_pacientes.html',{'pacientes': pacientes})

def agregar_paciente_admin(request):
    # lógica de la vista
    return render(request, 'agregar_paciente_admin.html')

def listar_pacientes_activos(request):
    # Obtener todos los pacientes activos
    pacientes_activos = Paciente.objects.filter(is_active=True)
    return render(request, 'admin_pacientes.html', {
        'pacientes': pacientes_activos,
        'estado': 'activos',
    })
def cambiar_estado_inactivo(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pacientes_ids = data.get('pacientes_ids', [])
        Paciente.objects.filter(id__in=pacientes_ids).update(is_active=False)
        return JsonResponse({'status': 'success'})

def restaurar_paciente(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pacientes_ids = data.get('pacientes_ids', [])
        Paciente.objects.filter(id__in=pacientes_ids).update(is_active=True)
        return JsonResponse({'status': 'success'})
        
def listar_pacientes_inactivos(request):
    # Obtener todos los pacientes inactivos
    pacientes_inactivos = Paciente.objects.filter(is_active=False)
    return render(request, 'admin_pacientes.html', {
        'pacientes': pacientes_inactivos,
        'estado': 'inactivos',
    })
########################################################
def admin_recepcionistas(request):
    # Lógica para listar o gestionar recepcionistas desde la vista del administrador
    return render(request, 'admin_recepcionistas.html')
def admin_terapeutas(request):
    return render (request,'admin_terapeutas.html')

def logout_view(request):
    # Lógica para cerrar la sesión
    # Puedes usar Django's auth logout
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')  # Redirigir al login después de cerrar sesión

@role_required('Administrador')
def agregar_terapeuta(request):
    if request.method == 'POST':
        terapeuta_form = CrearTerapeutaForm(request.POST)
        horario_formset = HorarioFormSet(request.POST)

        if terapeuta_form.is_valid() and horario_formset.is_valid():
            with transaction.atomic(): # Para que si algo falla, no se guarde nada, asegura que todas las operaciones se realicen correctamente
                terapeuta = terapeuta_form.save()
                horario_formset.instance = terapeuta # Asignamos el terapeuta a los horarios
                horario_formset.save()
            
            return redirect('gestion_terapeutas') # Redirigimos a la vista de gestión de terapeutas
        
    else:
        terapeuta_form = CrearTerapeutaForm()
        horario_formset = HorarioFormSet()
    
    return render(request, 'agregar_terapeuta.html', {
        'terapeuta_form': terapeuta_form,
        'horario_formset': horario_formset
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
    return render(request, 'mostrar_paciente_administrador.html', {'paciente': paciente})

@role_required('Administrador')
def listado_terapeutas(request, paciente_id):
    paciente = Paciente.objects.get(id=paciente_id)
    terapeuta = Terapeuta.objects.all()
    return render(request, 'listado_terapeutas.html', {'terapeuta': terapeuta, 'paciente': paciente})

@role_required('Administrador')
def calendar_asignar_paciente_administrador(request, terapeuta_id, paciente_id):
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
                                                              'paciente':paciente, 'terapeuta':terapeuta})
@role_required('Administrador')
def agendar_cita_administrador(request):
    if request.method == 'POST':
        titulo = request.POST['titulo']
        terapeuta_id = request.POST['terapeuta']
        paciente_id = request.POST['paciente']
        fecha = request.POST['fecha']
        hora = request.POST['hora']
        sala = request.POST['sala']
        detalle = request.POST['detalle']
    
        terapeuta_instance = Terapeuta.objects.get(id=terapeuta_id)
        
        paciente_instance = Paciente.objects.get(id=paciente_id)
        print(paciente_instance)
        
        cita = Cita(
            terapeuta = terapeuta_instance,
            titulo = titulo,
            paciente = paciente_instance,
            fecha = fecha,
            hora = hora,
            sala = sala,
            detalle = detalle
        )
        cita.save()
        
        #Guardar la asignación del terapeuta al paciente
        
        paciente_instance.terapeuta_id = terapeuta_instance.id
        paciente_instance.save()
        
        return redirect('mostrar_paciente_administrador', paciente_instance.id)
    return render(request, 'mostrar_paciente_administrador.html', {'paciente': paciente_instance})

def editar_datos_paciente_admin(request, id):
    paciente = get_object_or_404(Paciente, id=id)
    # guarda cambios
    if request.method == 'POST':
        paciente.first_name = request.POST.get('first_name')
        paciente.last_name = request.POST.get('last_name')
        paciente.rut = request.POST.get('rut')
        paciente.telefono = request.POST.get('telefono')
        paciente.correo = request.POST.get('correo')
        paciente.sexo = request.POST.get('sexo')
        paciente.date = request.POST.get('date')
        paciente.patologia = request.POST.get('patologia')
        paciente.terapeuta = request.POST.get('terapeuta')
        paciente.save()
        return redirect('admin_pacientes')

    return render(request, 'editar_datos_paciente_admin.html', {'paciente': paciente})
