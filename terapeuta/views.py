from random import randrange
from django.shortcuts import render, redirect
from autenticacion.decorators import role_required
from .models import Cita, Terapeuta, Paciente, Rutina
from .models import Cita, Terapeuta, Paciente, Observacion
from django.http import HttpResponse
from django.core.paginator import Paginator
from datetime import date
from django.http import JsonResponse
import json
from django.db.models import Q
from .models import Paciente, Rutina, Sesion, Corriente
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib import messages
import re
from django.core.files.storage import FileSystemStorage



#-------------------------------------AGENDA-------------------------------------

@login_required
@role_required('Terapeuta')
def agenda(request):
    # Datos para renderizar el select de pacientes en los Popup
    user_id = request.user.id
    try:
        terapeuta = Terapeuta.objects.get(user_id=user_id)
    except Terapeuta.DoesNotExist:
        messages.error(request, "No tienes un perfil de Terapeuta asociado.")
        return redirect('perfil')  # Redirige a una página adecuada

    terapeuta_id = terapeuta.id
    pacientes = Paciente.objects.filter(terapeuta_id=terapeuta_id)  # Obtener los pacientes del terapeuta

    # Obtención de las citas
    citas = Cita.objects.all()
    citas_json = []
    for cita in citas:
        if cita.paciente and cita.paciente.id and cita.paciente.first_name and cita.paciente.last_name:
            citas_json.append({
                'id': cita.id,  # Añadimos el ID de la cita
                'fecha': cita.fecha.strftime('%Y-%m-%d'),
                'titulo': cita.titulo,
                'hora_inicio': cita.hora_inicio.strftime('%H:%M'),
                'hora_final': cita.hora_final.strftime('%H:%M'),
                'detalle': cita.detalle,
                'sala': cita.sala,
                'paciente': {
                    'id': cita.paciente.id,
                    'nombre': f'{cita.paciente.first_name} {cita.paciente.last_name}'
                },
            })
        else:
            continue
    fechas_citas = json.dumps(citas_json)
    return render(request, 'agenda.html', {'pacientes': pacientes, 'fechas_citas': fechas_citas, 'citas': citas})

def obtener_fechas_citas(request):
    if request.method == "GET":
        citas = Cita.objects.all()
        citas_list = []
        for cita in citas:
            citas_list.append({
                'id': cita.id,
                'fecha': cita.fecha.strftime('%Y-%m-%d'),
                'titulo': cita.titulo,
                'hora_inicio': cita.hora_inicio.strftime('%H:%M'),
                'hora_final': cita.hora_final.strftime('%H:%M'),
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
@role_required('Terapeuta')
def pacientes_view(request):
    query = request.GET.get('search')  # Obtiene el parámetro de búsqueda desde el GET
    order_by = request.GET.get('order_by', 'first_name')  # Obtiene el parámetro de orden desde el GET
    
    # Filtra los pacientes asignados al terapeuta que inició sesión
    try:
        terapeuta = Terapeuta.objects.get(user=request.user)
    except Terapeuta.DoesNotExist:
        # Si el terapeuta no existe, retorna un error o redirecciona
        return render(request, 'error.html', {'mensaje': 'Terapeuta no encontrado.'})

    pacientes_list = Paciente.objects.filter(is_active=True, terapeuta=terapeuta)

    # Si hay una búsqueda, filtrar los pacientes
    if query:
        pacientes_list = pacientes_list.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(rut__icontains=query) | 
            Q(patologia__icontains=query)
        )

    # Calcular la edad de cada paciente
    pacientes_con_edad = []
    for paciente in pacientes_list:
        paciente.edad = calcular_edad(paciente.fecha_nacimiento)
        pacientes_con_edad.append(paciente)

    # Ordenar la lista de pacientes con edad calculada
    if order_by == 'edad':
        pacientes_con_edad.sort(key=lambda x: x.edad)  # Ordena por edad
    else:
        pacientes_con_edad.sort(key=lambda x: getattr(x, order_by))  # Ordena por otros campos

    total_pacientes = len(pacientes_con_edad)  # Cuenta la cantidad total de pacientes

    # Implementar la paginación
    paginator = Paginator(pacientes_con_edad, 5)  # Muestra 5 pacientes por página
    page_number = request.GET.get('page')  # Obtiene el número de la página de la URL
    pacientes = paginator.get_page(page_number)  # Obtiene los pacientes de la página actual
    
    return render(request, 'paciente_terapeuta.html', {
        'pacientes': pacientes, 
        'total_pacientes': total_pacientes,
        'query': query,  # Para mantener el valor en el HTML
        'order_by': order_by  # Para saber el orden actual en el HTML
    })


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

@login_required
def historial_paciente_view(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    paciente.edad = calcular_edad(paciente.fecha_nacimiento)

    # Intentar obtener el Terapeuta asociado al usuario
    try:
        terapeuta = Terapeuta.objects.get(user=request.user)
    except Terapeuta.DoesNotExist:
        terapeuta = None

    # Verificar si el usuario es terapeuta o superusuario
    if terapeuta or request.user.is_superuser:
        # Obtiene las rutinas del paciente, ordenadas por fecha de inicio
        rutinas = Rutina.objects.filter(paciente=paciente).order_by('-fecha_inicio')

        # Obtener las sesiones relacionadas con cada rutina
        for rutina in rutinas:
            # Obtiene las últimas dos sesiones de la rutina, ordenadas por fecha de sesión
            rutina.ultimas_sesiones = Sesion.objects.filter(rutina=rutina).order_by('-fecha')[:2]

        context = {
            'paciente': paciente,
            'terapeuta': terapeuta,
            'rutinas': rutinas,
        }
        return render(request, 'historial_paciente.html', context)
    else:
        # Si el usuario no es terapeuta ni superusuario, mostrar mensaje de error o redirigir
        return render(request, 'error.html', {'mensaje': 'No tienes permiso para acceder a esta página.'})

def obtener_grafico_sesion_paciente(request, sesion_id):
    sesion = get_object_or_404(Sesion, id=sesion_id)
    
    # Obtener todas las corrientes de la sesion
    corrientes = Corriente.objects.filter(sesion=sesion).order_by('hora')

    # Listas para almacenar las horas y corrientes de las sesiones
    horas = []
    corrientes_data = []  # Cambié el nombre para no sobrescribir

    # Extraer datos de cada corriente
    for corriente in corrientes:
        horas.append(corriente.hora.strftime('%H:%M'))  # Convertir la hora a string
        corrientes_data.append(corriente.corriente)  # Asumiendo que cada corriente tiene un campo 'valor'

    chart = {
        'xAxis': {
            'type': 'category',
            'data': horas,  # Horas de las corrientes
        },
        'yAxis': {
            'type': 'value',
            'name': 'Corriente (mA)'  # Etiqueta del eje Y para las corrientes
        },
        'series': [
            {
                'name': 'Corriente',
                'data': corrientes_data,
                'type': 'line',  # Gráfico de línea para corrientes
                'itemStyle': {
                    'color': '#FF7F50'  # Color personalizado
                }
            }
        ],
        'tooltip': {
            'trigger': 'axis',
            'formatter': '{b}<br />Corriente: {c} mA',  # Formato del tooltip
        },
        'legend': {
            'data': ['Corriente'],
            'selectedMode': False,   # Deshabilitar interacción para ocultar la línea
            'top': '5%'  # Asegura que la leyenda se vea bien en pantallas pequeñas
        }
    }

    return JsonResponse({'chart': chart})


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
            hora_inicio = request.POST['hora_inicio']
            hora_final = request.POST['hora_final']
            sala = request.POST['sala']
            detalle = request.POST['detalle']
        
            terapeuta_instance = Terapeuta.objects.get(id=terapeuta_id)
            
            paciente_instance = Paciente.objects.get(id=paciente_id)
            
            cita = Cita(
                terapeuta = terapeuta_instance,
                titulo = titulo,
                paciente = paciente_instance,
                fecha = fecha,
                hora_inicio = hora_inicio,
                hora_final = hora_final,
                sala = sala,
                detalle = detalle
            )
            cita.save()
            
            return redirect('agenda')
    return render(request, 'agenda.html')

@login_required  # Asegúrate de que el usuario esté autenticado
def calendar(request):
    return render(request, 'calendar.html')

def editar_cita(request):
    if request.method == "POST":
        cita_id = request.POST["cita_id"]
        cita = Cita.objects.get(id=cita_id)
        cita.titulo = request.POST["titulo_editar"]
        cita.paciente = Paciente.objects.get(id=request.POST["paciente_editar"])
        cita.fecha = request.POST["fecha_editar"]
        cita.hora_inicio = request.POST["hora_inicio_editar"]
        cita.hora_final = request.POST["hora_final_editar"]
        cita.sala = request.POST["sala_editar"]
        cita.detalle = request.POST["detalle_editar"]
        cita.save()
        return redirect("agenda")

    return agenda(request)


def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    
    # Lógica para eliminar la cita
    cita.delete()
    
    # Redirigir a la página de citas o donde desees
    return redirect('agenda')

################################################### GRÁFICOS PACIENTES ###################################################

def grafico_progreso_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    return render(request, 'grafico_progreso_paciente.html', {'paciente': paciente})

def obtener_grafico_progreso_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Obtener la rutina activa del paciente
    rutina_actual = Rutina.objects.filter(paciente=paciente).order_by('-fecha_inicio').first()

    # Si no hay rutina activa, devolver un mensaje
    if rutina_actual is None:
        return JsonResponse({'mensaje': 'El paciente no tiene ninguna rutina activa.'}, status=200)

    # Obtener todas las sesiones de la rutina actual
    sesiones = Sesion.objects.filter(rutina=rutina_actual).order_by('fecha')

    # Listas para almacenar las fechas, ángulos y velocidades de las sesiones
    fechas = []
    angulos_min = []
    angulos_max = []
    velocidades = []  # Lista para almacenar las velocidades

    # Extraer datos de cada sesión
    for sesion in sesiones:
        fechas.append(sesion.fecha.strftime('%Y-%m-%d'))  # Convertir la fecha a string
        angulos_min.append(sesion.angulo_min)
        angulos_max.append(sesion.angulo_max)
        velocidades.append(sesion.velocidad)  # Asumiendo que cada sesión tiene un campo 'velocidad'

    # Crear el objeto de configuración del gráfico en formato JSON
    chart = {
        'xAxis': {
            'type': 'category',
            'data': fechas,  # Fechas de las sesiones
        },
        'yAxis': {
            'type': 'value',
            'name': 'Ángulo (grados)'  # Etiqueta del eje Y para los ángulos
        },
        'series': [
            {
                'name': 'Ángulo Mínimo',
                'data': angulos_min,
                'type': 'line',  # Gráfico de línea para ángulos mínimos
                'itemStyle': {
                    'color': '#FF7F50'  # Color personalizado
                }
            },
            {
                'name': 'Ángulo Máximo',
                'data': angulos_max,
                'type': 'line',  # Gráfico de línea para ángulos máximos
                'itemStyle': {
                    'color': '#87CEFA'  # Color personalizado
                }
            }
        ],
        'tooltip': {
            'trigger': 'axis',
            'formatter': '{b}<br />Mín: {c0}°<br />Máx: {c1}°',  # Formato compacto
        },
        'legend': {
            'data': ['Ángulo Mínimo', 'Ángulo Máximo'],  # Leyenda del gráfico
            'top': '5%'  # Asegura que la leyenda se vea bien en pantallas pequeñas
        }
    }

    # Crear un segundo objeto para el gráfico de velocidad
    chart_velocidad = {
        'xAxis': {
            'type': 'category',
            'data': fechas,  # Fechas de las sesiones
        },
        'yAxis': {
            'type': 'value',
            'name': 'Velocidad (m/s)'  # Etiqueta del eje Y para la velocidad
        },
        'series': [
            {
                'name': 'Velocidad',
                'data': velocidades,
                'type': 'line',  # Gráfico de línea para la velocidad
                'itemStyle': {
                    'color': '#32CD32'  # Color personalizado para velocidad
                }
            }
        ],
        'tooltip': {
            'trigger': 'axis',
            'formatter': '{b}<br />v: {c} m/s'  # Formato del tooltip para velocidad
        },
        'legend': {
            'data': ['Velocidad'],  # Leyenda del gráfico de velocidad
            'selectedMode': False   # Deshabilitar interacción para ocultar la línea
        }
    }

    # Devolver ambos gráficos en la respuesta
    return JsonResponse({'chart': chart, 'chart_velocidad': chart_velocidad})

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
    
def obtener_datos_rutina(request, rutina_id):
    try:
        rutina = Rutina.objects.get(id=rutina_id)
        data = {
            'status': 'success',
            'rutina': {
                'fecha_inicio': rutina.fecha_inicio.strftime('%Y-%m-%d'),
                'angulo_inicial': rutina.angulo_inicial,
                'angulo_final': rutina.angulo_final,
                'repeticiones': rutina.repeticiones,
                'velocidad': rutina.velocidad,
                # Agrega otros campos que sí existan en el modelo
            }
        }
        return JsonResponse(data)
    except Rutina.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Rutina no encontrada'}, status=404)


@login_required
def editar_rutina(request, rutina_id):
    if request.method == 'POST':
        try:
            rutina = Rutina.objects.get(id=rutina_id)

            # Obtener y validar los datos
            fecha_inicio_str = request.POST.get('fecha_inicio')
            angulo_inicial_str = request.POST.get('angulo_inicial')
            angulo_final_str = request.POST.get('angulo_final')
            velocidad_str = request.POST.get('velocidad')
            repeticiones_str = request.POST.get('repeticiones')

            # Convertir a los tipos correctos
            from datetime import datetime
            rutina.fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            rutina.angulo_inicial = int(angulo_inicial_str)
            rutina.angulo_final = int(angulo_final_str)
            rutina.velocidad = int(velocidad_str)
            rutina.repeticiones = int(repeticiones_str)

            # Recalcular fecha de término si es necesario
            # Aquí puedes agregar lógica para fecha_termino

            rutina.save()

            return JsonResponse({'status': 'success'})
        except ValueError as e:
            print("Error de conversión:", e)
            return JsonResponse({'status': 'error', 'message': 'Datos inválidos: ' + str(e)}, status=400)
        except Rutina.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Rutina no encontrada'}, status=404)
        except Exception as e:
            print("Error al actualizar la rutina:", e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


def observaciones_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Obtener las observaciones relacionadas con el paciente, ordenadas por fecha
    observaciones = Observacion.objects.filter(paciente=paciente).order_by('-fecha')
    context = {
        'paciente': paciente,
        'observaciones': observaciones,
        'fecha_actual': now().strftime('%d/%m/%Y')
    }

    return render(request, 'registrar_observaciones.html', context)

@role_required('Terapeuta')
def agregar_observacion(request, paciente_id):
    if request.user.is_authenticated:
        user_id = request.user.id
        terapeuta = Terapeuta.objects.get(user_id=user_id)
        
        if request.method == 'POST':
            contenido = request.POST['contenido']
            paciente = get_object_or_404(Paciente, id=paciente_id)
            
            # Crear una nueva observación
            nueva_observacion = Observacion(
                paciente=paciente,
                contenido=contenido,
                fecha=timezone.now()
            )
            nueva_observacion.save()

            return redirect('observaciones_paciente', paciente_id=paciente.id)

    return redirect('historial_paciente', paciente_id=paciente_id)

@role_required('Terapeuta')
def editar_observacion(request, observacion_id):
    observacion = get_object_or_404(Observacion, id=observacion_id)
    
    if request.method == 'POST':
        contenido = request.POST['contenido']
        observacion.contenido = contenido
        observacion.save()
        
        return redirect('observaciones_paciente', paciente_id=observacion.paciente.id)

    return render(request, 'editar_observacion.html', {'observacion': observacion})

@role_required('Terapeuta')
def eliminar_observacion(request, observacion_id):
    if request.method == 'POST':
        observacion = get_object_or_404(Observacion, id=observacion_id)
        observacion.delete()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

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
        imagen = request.FILES.get('imagen_perfil')
        eliminar_imagen = request.POST.get('eliminar_imagen')

        try:
            # valida el correo
            validar_correo(nuevo_correo)
            if Terapeuta.objects.filter(correo_contacto=nuevo_correo).exclude(pk=terapeuta.pk).exists():
                messages.error(request, 'El correo ya está en uso por otro terapeuta.')
            else:
                # Actualiza los datos del terapeuta
                terapeuta.presentacion = nueva_presentacion
                terapeuta.correo_contacto = nuevo_correo

                # Manejo de la imagen de perfil
                if eliminar_imagen:
                    if terapeuta.imagen_perfil:
                        terapeuta.imagen_perfil.delete()
                    terapeuta.imagen_perfil = None
                elif imagen:
                    terapeuta.imagen_perfil = imagen

                terapeuta.save()
                messages.success(request, 'Perfil actualizado exitosamente.')
                return redirect('perfil')

        except ValidationError as e:
            messages.error(request, str(e))

    context = {
        'terapeuta': terapeuta,
    }
    return render(request, 'perfil.html', context)
    
def validar_correo(correo):
    # Expresión regular para validar el formato del correo
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(patron, correo):
        raise ValidationError("Introduzca una dirección de correo electrónico válida.")
    
    


def historial_sesiones(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    rutinas = Rutina.objects.filter(paciente=paciente).order_by('-fecha_inicio')
    
    # Obtener el parámetro 'rutina_id' de la URL
    rutina_id = request.GET.get('rutina_id')
    if rutina_id:
        rutina_seleccionada = get_object_or_404(Rutina, id=rutina_id, paciente=paciente)
    else:
        rutina_seleccionada = rutinas.first()  # Selecciona la rutina más reciente si no se especifica
    
    # Obtener las sesiones de la rutina seleccionada
    sesiones = Sesion.objects.filter(rutina=rutina_seleccionada).order_by('-fecha')
    
    context = {
        'paciente': paciente,
        'rutinas': rutinas,
        'rutina_seleccionada': rutina_seleccionada,
        'sesiones': sesiones,
    }
    return render(request, 'historial_sesiones.html', context)


