from django.urls import path
from . import views

urlpatterns = [
    path('administrador/gestion_terapeutas/', views.gestion_terapeutas, name='gestion_terapeutas'),
    path('base_admin/', views.base_admin_view, name='base_admin'),
    path('admin_pacientes/', views.admin_pacientes, name='admin_pacientes'),
    path('listar_pacientes_activos/', views.listar_pacientes_activos, name='listar_pacientes_activos'),
    path('listar_pacientes_inactivos/', views.listar_pacientes_inactivos, name='listar_pacientes_inactivos'),
    path('admin_pacientes/inactivar/', views.cambiar_estado_inactivo, name='cambiar_estado_inactivo'),
    path('admin_pacientes/restaurar/', views.restaurar_paciente, name='restaurar_paciente'),
    path('admin_recepcionistas/', views.admin_recepcionistas, name='admin_recepcionistas'),
    path('admin_terapeutas/',views.admin_terapeutas, name='admin_terapeutas'),
    path('logout/', views.logout_view, name='logout'),  # Para cerrar sesión
    path('agregar/', views.agregar_paciente_admin, name='agregar_paciente_admin'),
    path('administrador/agregar_terapeuta/', views.agregar_terapeuta, name='agregar_terapeuta'),
    path('api/provincias/', views.provincias_api, name='provincias_api'),
    path('api/comunas/', views.comunas_api, name='comunas_api'),
    path('mostrar_paciente_administrador/<int:paciente_id>', views.mostrar_paciente_administrador, name='mostrar_paciente_administrador'),
    path('listado_terapeutas/<int:paciente_id>', views.listado_terapeutas, name='listado_terapeutas'),
    path('calendar_asignar_paciente_administrador/<int:paciente_id>/<int:terapeuta_id>', views.calendar_asignar_paciente_administrador, name='calendar_asignar_paciente_administrador'),
    path('agendar_cita_administrador/<int:paciente_id>//<int:terapeuta_id>/',views.agendar_cita_administrador, name='agendar_cita_administrador' ),
    path('elegir_terapeuta_administrador/<int:paciente_id>/', views.elegir_terapeuta_administrador, name='elegir_terapeuta_administrador'),
    path('asignar_terapeuta_administrador/<int:paciente_id>//<int:terapeuta_id>/', views.asignar_terapeuta_administrador, name='asignar_terapeuta_administrador'),
    path('mostrar_paciente_con_terapeuta/<int:paciente_id>//<int:terapeuta_id>/', views.mostrar_paciente_con_terapeuta, name='mostrar_paciente_con_terapeuta'),
    path('mostrar_paciente_sin_terapeuta/<int:paciente_id>/', views.mostrar_paciente_sin_terapeuta, name='mostrar_paciente_sin_terapeuta'),
    path('editar_datos_paciente_admin/<int:paciente_id>', views.editar_datos_paciente_admin, name='editar_datos_paciente_admin'),
    path('redirigir_asignar_cita/<int:terapeuta_id>/<int:paciente_id>/', views.redirigir_asignar_cita, name='redirigir_asignar_cita'),
    path('calendar_asignar_paciente_administrador/<int:terapeuta_id>/<int:paciente_id>', views.calendar_asignar_paciente_administrador, name='calendar_asignar_paciente_administrador'),
    path('agendar_cita_administrador/',views.agendar_cita_administrador, name='agendar_cita_administrador' )
]