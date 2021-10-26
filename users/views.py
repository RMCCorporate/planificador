from django.shortcuts import render, redirect
from django.contrib.auth import logout as do_logout
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as do_login
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model


def welcome(request):
    if request.user.is_authenticated:
        return render(request, "login/welcome.html")
    return redirect("/login")


def register(request):
    return render(request, "login/register.html")


def login(request):
    form = AuthenticationForm()
    if request.method == "POST":
        # Añadimos los datos recibidos al formulario
        form = AuthenticationForm(data=request.POST)
        # Si el formulario es válido...
        if form.is_valid():
            # Recuperamos las credenciales validadas
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            # Verificamos las credenciales del usuario
            user = authenticate(username=username, password=password)
            usuario = get_user_model().objects.get(correo=str(user))
            # Si existe un usuario con ese nombre y contraseña
            if user is not None:
                # Hacemos el login manualmente

                if (
                    usuario.session_key
                ):  # check if user has session_key. This will be true for users logged in on another device
                    try:
                        s = Session.objects.get(session_key=usuario.session_key)
                    except Session.DoesNotExist:
                        pass
                    else:
                        s.delete()  # delete the old session_key from db

                do_login(request, user)
                # set new session_key for user instance
                usuario.session_key = request.session.session_key
                usuario.save()  # save the user
                # Y le redireccionamos a la portada

                # log the user in
                return redirect("/")
        else:
            messages.info(request, "Usuario o contraseña es incorrecta")

    # Si llegamos al final renderizamos el formulario
    return render(request, "login/login.html", {"form": form})


def logout(request):
    # Redireccionamos a la portada
    usuario = get_user_model().objects.get(nickname=str(request.user))
    usuario.session_key = None
    usuario.save()
    do_logout(request)
    # usuario = Usuario.objects.get(correo=re)
    return redirect("login")
