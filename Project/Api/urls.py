from django.urls import path
from .views import (
    Inicio,
    Contratar,
    Pago,
    Registro,
    Login,
    Panel,
    Logout,
    CrearServidor,
    EliminarServidor,
    AdministrarServidor,
    EncenderServidor,
    ApagarServidor,
    Pago,
    Contacto
)

urlpatterns = [
    path("", Inicio, name="Inicio"),

    # Cuenta
    path("login/", Login, name="Login"),
    path("logout/", Logout, name="Logout"),
    path("registro/", Registro, name="Registro"),
    path("contacto/", Contacto, name="Contacto"),

    # Contratación
    path("contratar/", Contratar, name="Contratar"),
    path("pago/", Pago, name="Pago"),

    # Panel
    path("panel/", Panel, name="Panel"),

    # Servidores
    path("crear-servidor/", CrearServidor, name="CrearServidor"),
    path("servidores/<int:servidor_id>/",AdministrarServidor,name="AdministrarServidor",),
    path("servidores/<int:servidor_id>/eliminar/",EliminarServidor,name="EliminarServidor",),
    path("servidores/<int:servidor_id>/encender/",EncenderServidor,name="EncenderServidor",),
    path("servidores/<int:servidor_id>/apagar/",ApagarServidor,name="ApagarServidor",),
]