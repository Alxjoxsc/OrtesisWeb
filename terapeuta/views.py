from django.shortcuts import render, redirect
from autenticacion.decorators import role_required
from .models import Cita, Terapeuta, Paciente, Rutina
from django.http import HttpResponse
from django.core.paginator import Paginator
from datetime import date
from django.http import JsonResponse
import json
from django.db.models import Q
from .models import Paciente
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

@role_required('Terapeuta')

#-------------------------------------AGENDA-------------------------------------
def agenda(request):
    paciente = Paciente.objects.all()
    citas = Cita.objects.all()
    citas_json = []
    for cita in citas:
        if cita.paciente and cita.paciente.id and cita.paciente.first_name and cita.paciente.last_name:
            citas_json.append({
                'id': cita.id,  # Añadimos el ID de la cita
                'fecha': cita.fecha.strftime('%Y-%m-%d'),
                'titulo': cita.titulo,
                'hora': cita.hora.strftime('%H:%M'),
                'descripcion': cita.detalle,
                'paciente': {
                    'id': cita.paciente.id,
                    'nombre': f'{cita.paciente.first_name} {cita.paciente.last_name}'
                }
            })
        else:
            continue
    context = {
        'paciente': Paciente.objects.all(),
        'fechas_citas': json.dumps(citas_json)
    }
    return render(request, 'agenda.html', context)
    return render(request, 'agenda.html', {'paciente':paciente})

def obtener_fechas_citas(request):
    if request.method == "GET":
        citas = Cita.objects.all()
        citas_list = []
        for cita in citas:
            citas_list.append({
                'id': cita.id,
                'fecha': cita.fecha.strftime('%Y-%m-%d'),
                'titulo': cita.titulo,
                'hora': cita.hora.strftime('%H:%M'),
                'descripcion': cita.detalle,
                'paciente': {
                    'id': cita.paciente.id,
                    'nombre': f'{cita.paciente.first_name} {cita.paciente.last_name}'
                }
            })
        return JsonResponse({'citas': citas_list})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
@role_required('Terapeuta')

#-------------------------------------PERFIL-------------------------------------
def perfil_view(request):
    return render(request, 'perfil.html')

def calcular_edad(fecha_nacimiento):
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))


#-------------------------------------PACIENTES-------------------------------------
def pacientes_view(request):
    query = request.GET.get('search')  # Obtiene el parámetro de búsqueda desde el GET
    pacientes_list = Paciente.objects.filter(is_active=True)

    # Si hay una búsqueda, filtrar los pacientes
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

    total_pacientes = pacientes_list.count()  # Cuenta la cantidad total de pacientes

    # Implementar la paginación
    paginator = Paginator(pacientes_list, 6)  # Muestra 6 pacientes por página
    page_number = request.GET.get('page')  # Obtiene el número de la página de la URL
    pacientes = paginator.get_page(page_number)  # Obtiene los pacientes de la página actual
    
    return render(request, 'paciente_terapeuta.html', {'pacientes': pacientes, 'total_pacientes': total_pacientes})

@role_required('Terapeuta')
def cambiar_estado_paciente(request, id):
    if request.method == "POST":
        try:
            paciente = Paciente.objects.get(id=id)
            data = json.loads(request.body)  # Cargar el JSON enviado desde el frontend
            motivo_desvinculacion = data.get("motivo", "")  # Obtener el motivo del JSON
            
            if motivo_desvinculacion.strip() == "":
                return JsonResponse({"status": "error", "message": "Motivo de inactivación requerido."}, status=400)

            paciente.is_active = False
            paciente.motivo_desvinculacion = motivo_desvinculacion  # Guardar el motivo de la inactivación
            paciente.save()

            return JsonResponse({"status": "success", "message": "Paciente inactivado correctamente."})
        except Paciente.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Paciente no encontrado"}, status=404)
    return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)

def historial_paciente_view(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    terapeuta = get_object_or_404(Terapeuta, user=request.user)
    paciente.edad = calcular_edad(paciente.fecha_nacimiento)
    rutinas = Rutina.objects.filter(paciente=paciente).order_by('-fecha_inicio')
    context = {'paciente': paciente,
               'terapeuta': terapeuta,
               'rutinas': rutinas,
                }
    return render(request, 'historial_paciente.html', context)

#-------------------------------------CITAS-------------------------------------
@role_required('Terapeuta')
def agendar_cita(request):    
    if request.user.is_authenticated:
        user_id = request.user.id
        terapeuta = Terapeuta.objects.get(user_id=user_id)
        terapeuta_id = terapeuta.id
        print(terapeuta_id)
        if request.method == 'POST':
            titulo = request.POST['titulo']
            paciente_id = request.POST['paciente']
            fecha = request.POST['fecha']
            hora = request.POST['hora']
            sala = request.POST['sala']
            detalle = request.POST['detalle']
        
            terapeuta_instance = Terapeuta.objects.get(id=terapeuta_id)
            
            paciente_instance = Paciente.objects.get(id=paciente_id)
            
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
            
            return redirect('agenda')
    return render(request, 'agenda.html')

def calendar(request):
    paciente = Paciente.objects.all()
    print(paciente)
    return render (request, 'calendar.html', {'paciente':paciente})


def editar_cita(request):
    if request.method == "POST":
        cita_id = request.POST["cita_id"]
        cita = Cita.objects.get(id=cita_id)
        cita.titulo = request.POST["titulo"]
        cita.paciente = Paciente.objects.get(id=request.POST["paciente"])
        cita.fecha = request.POST["fecha"]
        cita.hora = request.POST["hora"]
        cita.sala = request.POST["sala"]
        cita.detalle = request.POST["detalle"]
        cita.save()
        return redirect("agenda")
    return render(request, "editar_cita.html")

def eliminar_cita(request, cita_id):
    if request.method == 'DELETE':
        try:
            cita = Cita.objects.get(id=cita_id)
            cita.delete()  # Elimina la cita de la base de datos
            return JsonResponse({'message': 'Cita eliminada exitosamente.'}, status=200)
        except Cita.DoesNotExist:
            return JsonResponse({'error': 'Cita no encontrada.'}, status=404)
    return JsonResponse({'error': 'Método no permitido.'}, status=405)

#-------------------------------------RUTINAS-------------------------------------

def crear_rutina(request, paciente_id):
    if request.method == 'POST':
        # Obtener los datos del formulario
        fecha_inicio = request.POST.get('fecha_inicio')
        cantidad_sesiones = request.POST.get('cantidad_sesiones')
        repeticiones = request.POST.get('repeticiones')
        frecuencia_cantidad = request.POST.get('frecuencia_cantidad')
        frecuencia_tipo = request.POST.get('frecuencia_tipo')
        angulo_inicial = request.POST.get('angulo_inicial')
        angulo_final = request.POST.get('angulo_final')
        velocidad = request.POST.get('velocidad')

        try:
            paciente = get_object_or_404(Paciente, id=paciente_id)
            terapeuta = get_object_or_404(Terapeuta, user=request.user)

            # Calcular la fecha de término
            from datetime import datetime, timedelta

            fecha_inicio_date = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            frecuencia_dias = int(frecuencia_cantidad) * (7 if frecuencia_tipo == 'semanas' else 1)
            total_duracion = (int(cantidad_sesiones) - 1) * frecuencia_dias
            fecha_termino_date = fecha_inicio_date + timedelta(days=total_duracion)

            # Crear la nueva rutina
            nueva_rutina = Rutina.objects.create(
                terapeuta=terapeuta,
                paciente=paciente,
                fecha_inicio=fecha_inicio_date,
                fecha_termino=fecha_termino_date,
                angulo_inicial=angulo_inicial,
                angulo_final=angulo_final,
                repeticiones=repeticiones,
                velocidad=velocidad,
                descripcion='',  # Puedes ajustar este campo si es necesario
            )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'})
    
def perfil(request):
    
    terapeuta = get_object_or_404(Terapeuta, user=request.user)
    
    context = {
        'terapeuta': terapeuta,
    }
    
    return render(request, 'perfil.html', context)

def editar_perfil(request, pk):
    terapeuta = get_object_or_404(Terapeuta, pk=pk)
    if request.method == 'POST':
        nueva_presentacion = request.POST.get('presentacion')
        nuevo_correo = request.POST.get('correo_contacto')
        
        terapeuta.presentacion = nueva_presentacion
        terapeuta.correo_contacto = nuevo_correo
        terapeuta.save()
        
        return redirect('perfil')