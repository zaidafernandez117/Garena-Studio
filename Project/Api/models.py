from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class SolicitudServidor(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    plan = models.CharField(max_length=50)
    metodo_pago = models.CharField(max_length=50, default="Pendiente")
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.plan} - {self.metodo_pago}"


class Servidor(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    plan = models.CharField(max_length=50)

    cpu = models.CharField(max_length=30, default="2 vCPU")
    ram = models.CharField(max_length=30, default="4 GB")
    almacenamiento = models.CharField(max_length=30, default="80 GB NVMe")
    ip = models.GenericIPAddressField(default="127.0.0.1")

    estado = models.CharField(max_length=20, default="Offline")
    fecha_creacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
class MensajeContacto(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    asunto = models.CharField(max_length=100)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.asunto}"
    
class PerfilUsuario(models.Model):
    usuario= models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    fecha_nacimiento = models.DateField()
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
    
class VerificacionCorreo(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    codigo = models.CharField(max_length=6)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    verificado = models.BooleanField(default=False)

    def __str__(self):
        return f"Verificación de {self.usuario.email}"