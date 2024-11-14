from django.contrib import admin
from .models import Recepcionista

@admin.register(Recepcionista)
class RecepcionistaAdmin(admin.ModelAdmin):
    list_display = ('user', 'fecha_contratacion', 'turno', 'experiencia', 'supervisor')
    search_fields = ('user__first_name', 'user__last_name', 'formacion_academica')
    list_filter = ('turno', 'supervisor', 'fecha_contratacion')
