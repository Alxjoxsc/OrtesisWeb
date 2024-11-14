from django.contrib import admin
from .models import Administrador

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('user', 'fecha_contratacion', 'departamento')
    search_fields = ('user__first_name', 'user__last_name', 'departamento')
    list_filter = ('fecha_contratacion', 'departamento')
