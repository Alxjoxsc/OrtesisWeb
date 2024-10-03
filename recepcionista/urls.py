from django.urls import path
from . import views

urlpatterns = [
    path('recepcionista_pacientes_activos', views.recepcionista_pacientes_activos, name='recepcionista_pacientes_activos'),
    path('recepcionista_pacientes_inactivos', views.recepcionista_pacientes_inactivos, name='recepcionista_pacientes_inactivos'),
    path('recepcionista_pacientes/inactivar', views.recepcionista_cambiar_estado_inactivo, name='recepcionista_cambiar_estado_inactivo'),
    path('recepcionista_pacientes/restaurar', views.recepcionista_restaurar_paciente, name='recepcionista_restaurar_paciente'),
    path('recepcionista_terapeutas_activos/', views.recepcionista_terapeutas_activos, name='recepcionista_terapeutas_activos'),
    path('agregar_paciente', views.agregar_paciente, name='agregar_paciente'),
    path('elegir_terapeuta/<int:id>/', views.elegir_terapeuta, name='elegir_terapeuta'),
    path('asignar_terapeuta/<int:paciente_id>//<int:terapeuta_id>/', views.asignar_terapeuta, name='asignar_terapeuta'),
    path('agendar_cita_recepcionista/', views.agendar_cita_recepcionista, name='agendar_cita_recepcionista'),
    #path('asignar_terapeuta_paciente', views.asignar_terapeuta_paciente, name ='asignar_terapeuta_paciente'),
    path('calendar_asignar_paciente/<int:paciente_id>//<int:terapeuta_id>/', views.calendar_asignar_paciente, name='calendar_asignar_paciente'),
    path('formulario_agregar_paciente', views.formulario_agregar_paciente, name='formulario_agregar_paciente'),
    path('mostrar_paciente_con_terapeuta/<int:paciente_id>//<int:terapeuta_id>/', views.mostrar_paciente_con_terapeuta, name='mostrar_paciente_con_terapeuta'),
    path('mostrar_paciente_sin_terapeuta/<int:paciente_id>/', views.mostrar_paciente_sin_terapeuta, name='mostrar_paciente_sin_terapeuta')

]