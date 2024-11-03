
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('autenticacion.urls')),
    path('', include('administrador.urls')),
    path('', include('terapeuta.urls')),
    path('', include('recepcionista.urls')),
    path("admin/", admin.site.urls),
]
