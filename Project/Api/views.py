from django.shortcuts import render
from .models import SolicitudServidor, Servidor, MensajeContacto
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from datetime import date
from .models import PerfilUsuario
import os
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from .models import VerificacionCorreo

def Inicio(request):
    return render(request, 'Inicio.html')

def Contratar(request):

    if request.method == "POST":

        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        plan = request.POST.get("plan")

        return redirect(
            f"/pago/?nombre={nombre}&email={email}&plan={plan}"
        )

    plan = request.GET.get("plan", "")

    email = request.user.email if request.user.is_authenticated else ""

    return render(request, "Contratar.html", {
        "plan_seleccionado": plan,
        "email": email
    })

def Registro(request):
    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        fecha_nacimiento = request.POST.get("fecha_nacimiento", "")

        if not all([username, email, password, fecha_nacimiento]):
            return render(request, "Registro.html", {
                "error": "Todos los campos son obligatorios."
            })

        if User.objects.filter(username__iexact=username).exists():
            return render(request, "Registro.html", {
                "error": "Ese usuario ya está registrado."
            })

        if User.objects.filter(email__iexact=email).exists():
            return render(request, "Registro.html", {
                "error": "Ese correo ya está registrado."
            })

        try:
            nacimiento = date.fromisoformat(fecha_nacimiento)
        except ValueError:
            return render(request, "Registro.html", {
                "error": "Ingresá una fecha válida."
            })

        hoy = date.today()

        if nacimiento > hoy:
            return render(request, "Registro.html", {
                "error": "La fecha no puede ser futura."
            })

        edad = hoy.year - nacimiento.year
        if (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day):
            edad -= 1

        if edad < 18:
            return render(request, "Registro.html", {
                "error": "Debés tener al menos 18 años."
            })

        usuario = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
        )

        PerfilUsuario.objects.create(
            usuario=usuario,
            fecha_nacimiento=nacimiento
        )

        codigo = str(int.from_bytes(os.urandom(4), "big") % 1000000).zfill(6)

        VerificacionCorreo.objects.create(
            usuario=usuario,
            codigo=codigo
        )

        try:
            send_mail(
                "Verificación de Garena Studio",
                f"Tu código de verificación es: {codigo}",
                None,
                [email],
                fail_silently=False
            )
        except Exception:
            usuario.delete()
            return render(request, "Registro.html", {
                "error": "No pudimos enviar el correo. Intentá nuevamente."
            })

        request.session["usuario_verificacion"] = usuario.id

        return redirect("VerificarCorreo")

    return render(request, "Registro.html")

def VerificarCorreo(request):
    usuario_id = request.session.get("usuario_verificacion")

    if not usuario_id:
        return redirect("Registro")

    usuario = get_object_or_404(User, id=usuario_id)

    if request.method == "POST":
        codigo_ingresado = request.POST.get("codigo", "").strip()

        verificacion = VerificacionCorreo.objects.filter(
            usuario=usuario,
            verificado=False
        ).order_by("-fecha_creacion").first()

        if not verificacion:
            return render(request, "VerificarCorreo.html", {
                "error": "No se encontró un código pendiente."
            })

        # El código vence después de 10 minutos.
        if timezone.now() - verificacion.fecha_creacion > timedelta(minutes=10):
            return render(request, "VerificarCorreo.html", {
                "error": "El código venció. Necesitás solicitar uno nuevo."
            })

        if codigo_ingresado != verificacion.codigo:
            return render(request, "VerificarCorreo.html", {
                "error": "El código ingresado es incorrecto."
            })

        verificacion.verificado = True
        verificacion.save()

        usuario.is_active = True
        usuario.save()

        del request.session["usuario_verificacion"]

        login(request, usuario)

        return redirect("Panel")

    return render(request, "VerificarCorreo.html")
    
@login_required(login_url="/login/")
def Pago(request):

    if request.method == "POST":

        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        plan = request.POST.get("plan")
        metodo_pago = request.POST.get("metodo_pago")

        SolicitudServidor.objects.create(
            usuario=request.user,
            nombre=nombre,
            plan=plan,
            metodo_pago=metodo_pago
        )

        return render(request, "Pago.html", {
            "pagado": True,
            "nombre": nombre,
            "email": email,
            "plan": plan,
            "metodo_pago": metodo_pago
        })

    nombre = request.GET.get("nombre", request.user.username)
    email = request.GET.get("email", request.user.email)
    plan = request.GET.get("plan", "")

    return render(request, "Pago.html", {
        "nombre": nombre,
        "email": email,
        "plan": plan
    })

def Login(request):

    next_url = request.GET.get("next", "")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next", "")

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            login(request, usuario)

            if next_url:
                return redirect(next_url)

            return redirect("Panel")

        return render(request, "Login.html", {
            "error": "Usuario o contraseña incorrectos.",
            "next": next_url
        })

    return render(request, "Login.html", {
        "next": next_url
    })


@login_required(login_url="/login/")
def Panel(request):

    servidores = Servidor.objects.filter(
        usuario=request.user
    )
    
    servidores_online = servidores.filter(estado="Online").count()

    solicitudes = SolicitudServidor.objects.filter(
        usuario=request.user
    ).order_by("-fecha")

    return render(request, "Panel.html", {
        "usuario": request.user,
        "servidores": servidores,
        "solicitudes": solicitudes
    })
    
@login_required(login_url="/login/")
def CrearServidor(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        plan = request.POST.get("plan")

        if plan == "Starter":
            cpu = "2 vCPU"
            ram = "4 GB"
            almacenamiento = "80 GB NVMe"

        elif plan == "Pro":
            cpu = "6 vCPU"
            ram = "16 GB"
            almacenamiento = "320 GB NVMe"

        elif plan == "Enterprise":
            cpu = "16 vCPU"
            ram = "64 GB"
            almacenamiento = "1 TB NVMe"

        else:
            cpu = "2 vCPU"
            ram = "4 GB"
            almacenamiento = "80 GB NVMe"

        Servidor.objects.create(
            usuario=request.user,
            nombre=nombre,
            plan=plan,
            cpu=cpu,
            ram=ram,
            almacenamiento=almacenamiento
        )

        return redirect("Panel")

    return render(request, "CrearServidor.html")

@login_required(login_url="/login/")
def EliminarServidor(request, servidor_id):
    if request.method == "POST":
        servidor = Servidor.objects.get(
            id=servidor_id,
            usuario=request.user
        )

        servidor.delete()

    return redirect("Panel")

@login_required(login_url="/login/")
def AdministrarServidor(request, servidor_id):
    servidor = Servidor.objects.get(
        id=servidor_id,
        usuario=request.user
    )

    return render(request, "AdministrarServidor.html", {
        "servidor": servidor
    })

def Logout(request):
    logout(request)
    return redirect("Login")

@login_required(login_url="/login/")
def EncenderServidor(request, servidor_id):
    if request.method == "POST":
        servidor = Servidor.objects.get(
            id=servidor_id,
            usuario=request.user
        )

        servidor.estado = "Online"
        servidor.save()

    return redirect("AdministrarServidor", servidor_id=servidor_id)


@login_required(login_url="/login/")
def ApagarServidor(request, servidor_id):
    if request.method == "POST":
        servidor = Servidor.objects.get(
            id=servidor_id,
            usuario=request.user
        )

        servidor.estado = "Offline"
        servidor.save()

    return redirect("AdministrarServidor", servidor_id=servidor_id)


def Contacto(request):
    if request.method =="POST":
        if request.user.is_authenticated:
            nombre = request.user.username
            email = request.user.email
            usuario = request.user
        else:
            nombre = request.POST.get("nombre")
            email = request.POST.get("email")
            usuario = None
            
            asunto = request.POST.get("asunto")
            mensaje = request.POST.get("mensaje")
            
            MensajeContacto.objects.create(
                usuario=usuario,
                nombre=nombre,
                email=email,
                asunto=asunto,
                mensaje=mensaje
            ) 
            
            return render(request,
                          "Contacto.html",{
                              "enviado: True"
                              })