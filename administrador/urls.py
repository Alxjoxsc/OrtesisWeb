from django.urls import path
from . import views

urlpatterns = [
    path('listar_terapeutas_activos/', views.listar_terapeutas_activos, name='listar_terapeutas_activos'),
    path('listar_terapeutas_inactivos/', views.listar_terapeutas_inactivos, name='listar_terapeutas_inactivos'),
    path('inactivar_terapeuta/', views.cambiar_estado_inactivo_terapeuta, name='cambiar_estado_inactivo_terapeuta'),
    path('restaurar_terapeuta/', views.restaurar_terapeuta, name='restaurar_terapeuta'),
    path('listar_pacientes_activos/', views.listar_pacientes_activos, name='listar_pacientes_activos'),
    path('listar_pacientes_inactivos/', views.listar_pacientes_inactivos, name='listar_pacientes_inactivos'),
    path('admin_pacientes/inactivar/', views.cambiar_estado_inactivo, name='cambiar_estado_inactivo'),
    path('admin_pacientes/restaurar/', views.restaurar_paciente, name='restaurar_paciente'),
    path('listar_recepcionistas_activos/', views.listar_recepcionistas_activos, name='listar_recepcionistas_activos'),
    path('listar_recepcionistas_inactivos/', views.listar_recepcionistas_inactivos, name='listar_recepcionistas_inactivos'),
    path('inactivar_recepcionista/', views.cambiar_estado_inactivo_recepcionista, name='cambiar_estado_inactivo_recepcionista'),
    path('restaurar_recepcionista/', views.restaurar_recepcionista, name='restaurar_recepcionista'),
    path('agregar/', views.agregar_paciente_admin, name='agregar_paciente_admin'),
    path('administrador/agregar_terapeuta/', views.agregar_terapeuta, name='agregar_terapeuta'),
    path('api/comunas/', views.comunas_api, name='comunas_api'),
    path('mostrar_paciente_administrador/<int:paciente_id>', views.mostrar_paciente_administrador, name='mostrar_paciente_administrador'),
    path('mostrar_recepcionista_administrador/<int:recepcionista_id>', views.mostrar_recepcionista_administrador, name='mostrar_recepcionista_administrador'),
    path('mostrar_terapeuta_administrador/<int:terapeuta_id>', views.mostrar_terapeuta_administrador, name='mostrar_terapeuta_administrador'),
    path('listado_terapeutas/<int:paciente_id>', views.listado_terapeutas, name='listado_terapeutas'),
    path('calendar_asignar_paciente_administrador/<int:paciente_id>/<int:terapeuta_id>', views.calendar_asignar_paciente_administrador, name='calendar_asignar_paciente_administrador'),
    path('agendar_cita_administrador/<int:paciente_id>//<int:terapeuta_id>/',views.agendar_cita_administrador, name='agendar_cita_administrador' ),
    path('elegir_terapeuta_administrador/<int:paciente_id>/', views.elegir_terapeuta_administrador, name='elegir_terapeuta_administrador'),
    path('asignar_terapeuta_administrador/<int:paciente_id>//<int:terapeuta_id>/', views.asignar_terapeuta_administrador, name='asignar_terapeuta_administrador'),
    path('mostrar_paciente_con_terapeuta/<int:paciente_id>//<int:terapeuta_id>/', views.mostrar_paciente_con_terapeuta, name='mostrar_paciente_con_terapeuta'),
    path('mostrar_paciente_sin_terapeuta/<int:paciente_id>/', views.mostrar_paciente_sin_terapeuta, name='mostrar_paciente_sin_terapeuta'),
    path('editar_datos_paciente_admin/<int:paciente_id>', views.editar_datos_paciente_admin, name='editar_datos_paciente_admin'),
    path('calendar_asignar_paciente_administrador/<int:terapeuta_id>/<int:paciente_id>', views.calendar_asignar_paciente_administrador, name='calendar_asignar_paciente_administrador'),
    path('agendar_cita_administrador/',views.agendar_cita_administrador, name='agendar_cita_administrador' ),
     path('verificar_password_admin/', views.verificar_password_admin, name='verificar_password_admin'),
    path('actualizar_email_terapeuta/', views.actualizar_email_terapeuta, name='actualizar_email_terapeuta'),
    path('actualizar_credenciales_terapeuta/', views.actualizar_credenciales_terapeuta, name='actualizar_credenciales_terapeuta'),
    path('actualizar_email_recepcionista/', views.actualizar_email_recepcionista, name='actualizar_email_recepcionista'),
    path('actualizar_credenciales_recepcionista/', views.actualizar_credenciales_recepcionista, name='actualizar_credenciales_recepcionista'),
]