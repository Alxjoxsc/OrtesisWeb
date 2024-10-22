from django.urls import path
from . import views
from terapeuta.views import *

urlpatterns = [
    path('agenda/', views.agenda, name='agenda'),
    path('agendar_cita', views.agendar_cita, name='agendar_cita'),
    path('pacientes_terapeuta/', views.pacientes_view, name='paciente_terapeuta'),
    path('calendar', views.calendar, name= 'calendar'),
    path('paciente/cambiar-estado/<int:id>/', views.cambiar_estado_paciente, name='cambiar_estado_paciente'),
    path("editar_cita/", views.editar_cita, name="editar_cita"),
    path("obtener-fechas-citas/", views.obtener_fechas_citas, name="obtener_fechas_citas"),
    path('historial-paciente/<int:paciente_id>/', views.historial_paciente_view, name='historial_paciente'),
    path('eliminar-cita/<int:cita_id>/', views.eliminar_cita, name='eliminar_cita'),
    path('grafico_progreso_paciente/<int:paciente_id>/', views.grafico_progreso_paciente, name='grafico_progreso_paciente'),
    path('obtener_grafico_progreso_paciente/<int:paciente_id>/', views.obtener_grafico_progreso_paciente, name='obtener_grafico_progreso_paciente'),
    path('paciente/<int:paciente_id>/crear_rutina/', views.crear_rutina, name='crear_rutina'),
    path('obtener_grafico_sesion_paciente/<int:sesion_id>/', views.obtener_grafico_sesion_paciente, name='obtener_grafico_sesion_paciente'),
    path('rutina/<int:rutina_id>/datos/', views.obtener_datos_rutina, name='obtener_datos_rutina'),
    path('rutina/<int:rutina_id>/editar/', views.editar_rutina, name='editar_rutina'),
    path('observaciones/<int:paciente_id>/', views.observaciones_paciente, name='observaciones_paciente'),
    path('paciente/<int:paciente_id>/agregar_observacion/', views.agregar_observacion, name='agregar_observacion'),
    path('editar-observacion/<int:observacion_id>/', views.editar_observacion, name='editar_observacion'),
    path('eliminar_observacion/<int:observacion_id>/', eliminar_observacion, name='eliminar_observacion'),
    path('perfil/', views.perfil, name='perfil'),
    path('editar_perfil/<int:pk>/', views.editar_perfil, name='editar_perfil'),
    path('historial_sesiones/<int:paciente_id>/', views.historial_sesiones, name='historial_sesiones'),
    path('obtener_rutinas/', views.obtener_rutinas, name='obtener_rutinas'),
]