from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_usuario, name='login'),
    path('elegir_rol/', views.elegir_rol, name='elegir_rol'),
    path('logout/', views.logout_usuario, name='logout'),
    path('acceso_denegado/', views.acceso_denegado, name='acceso_denegado'),
    path('', views.login_usuario, name='home'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', views.password_reset_done, name='password_reset_done'), 
    path('password_reset/confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password_reset/complete/', views.password_reset_complete, name='password_reset_complete'),
    path('password_reset/invalid/', views.invalid_token, name='invalid_token'),
]