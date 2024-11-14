from django.contrib import admin
from .models import Terapeuta

@admin.register(Terapeuta)
class TerapeutaAdmin(admin.ModelAdmin):
    list_display = ('user', 'especialidad', 'fecha_ingreso', 'disponibilidad', 'horas_trabajadas')
    search_fields = ('user__first_name', 'user__last_name', 'especialidad')
    list_filter = ('disponibilidad', 'fecha_contratacion')
