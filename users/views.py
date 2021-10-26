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
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            usuario = get_user_model().objects.get(correo=str(user))
            if user is not None:
                if (
                    usuario.session_key
                ):
                    try:
                        s = Session.objects.get(session_key=usuario.session_key)
                    except Session.DoesNotExist:
                        pass
                    else:
                        s.delete()

                do_login(request, user)
                usuario.session_key = request.session.session_key
                usuario.save()
                return redirect("/")
        else:
            messages.info(request, "Usuario o contraseña es incorrecta")
    return render(request, "login/login.html", {"form": form})


def logout(request):
    usuario = get_user_model().objects.get(correo=str(request.user))
    usuario.session_key = None
    usuario.save()
    do_logout(request)
    return redirect("login")
