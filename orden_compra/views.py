from django.shortcuts import render, redirect
from planificador.models import Orden_compra, Cotizacion, RMC, Producto_proyecto, Producto
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date, datetime
from planificador.decorators import allowed_users
import uuid


def crear_orden(request, id):
    cotizacion_padre = Cotizacion.objects.get(id=id)
    productos_proyecto = []
    for producto in cotizacion_padre.productos_asociados.all():
        producto_proyecto = Producto_proyecto.objects.get(producto=cotizacion_padre.proyecto_asociado, proyecto=producto)
        productos_proyecto.append(producto_proyecto)
    return render(request, "orden_compra/crear_orden.html", {"cotizacion_padre":cotizacion_padre, "productos":productos_proyecto})