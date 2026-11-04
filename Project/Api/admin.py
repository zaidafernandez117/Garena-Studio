from django.contrib import admin
from .models import SolicitudServidor, Servidor


@admin.register(SolicitudServidor)
class SolicitudServidorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "plan", "fecha")


@admin.register(Servidor)
class ServidorAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "usuario",
        "plan",
        "estado",
        "ip",
        "fecha_creacion",
    )