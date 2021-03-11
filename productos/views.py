from django.shortcuts import render
from django.http import HttpResponse
from planificador.models import Producto

#Mostrar productos
def productos(request):
    productos = Producto.objects.all()
    return render(request, "productos/productos.html", {"Productos":productos})

#Agregar producto
def agregar_producto(request):
    return render(request, "productos/crear_producto.html")

def recibir_datos_producto(request):
    id = request.GET["id"]
    nombre = request.GET["nombre"]
    clase = request.GET["clase"]
    sub_clase = request.GET["sub_clase"]
    unidad = request.GET["unidad"]
    nuevo_producto = Producto(id=id, nombre=nombre, clase=clase, subclase=sub_clase, unidad=unidad)
    nuevo_producto.save()
    mensaje = "Producto creado satisfactoriamente"
    return HttpResponse(mensaje)