from django.shortcuts import render
from django.http import HttpResponse
from planificador.models import Producto, Clase, SubClase, Precio
from datetime import date

#Mostrar productos
def productos(request):
    productos = Producto.objects.all()
    return render(request, "productos/productos.html", {"Productos":productos})

#Agregar producto
def agregar_producto(request):
    clases = Clase.objects.all()
    subclases = SubClase.objects.all()
    return render(request, "productos/crear_producto.html", {"Clases":clases, "Subclases":subclases})

def recibir_datos_producto(request):
    id = request.GET["id"]
    nombre = request.GET["nombre"]
    sub_clase = request.GET["subclase"]
    unidad = request.GET["unidad"]
    nuevo_producto = Producto(id=id, nombre=nombre, unidad=unidad)
    nuevo_producto.save()
    subclase = SubClase.objects.get(nombre=sub_clase)
    subclase.productos.add(nuevo_producto)
    productos = Producto.objects.all()
    return render(request, "productos/productos.html", {"Productos":productos})
   
#Vista producto
def producto(request, id):
    producto = Producto.objects.get(id=id)
    lista_precios = producto.lista_precios.all()
    sub_clase = producto.subclase_set.all()[0]
    clase = sub_clase.clase_set.all()[0]
    return render(request, "productos/producto.html", {"Producto":producto, "lista_precios":lista_precios, "Subclase":sub_clase, "Clase":clase})

#Edición producto
def mostrar_edicion_producto(request, id):
    producto = Producto.objects.get(id=id)
    if request.method == "POST":
        Precios = Precio.objects.all()
        for i in Precios:
            i.delete()
        producto.id = request.POST["id"]
        producto.nombre = request.POST["nombre"]
        producto.unidad = request.POST["unidad"]
        #Precios
        precio = request.POST["precio"]
        moneda = request.POST["moneda"]
        proveedor = request.POST["proveedor"]
        comentario = request.POST["comentario"]
        nuevo_precio = Precio(valor=precio, tipo_cambio=moneda, nombre_proveedor=proveedor, comentarios=comentario)
        nuevo_precio.save()
        producto.save()
        producto.lista_precios.add(nuevo_precio)
        productos = Producto.objects.all()
        return render(request, "productos/productos.html", {"Productos":productos})
    else:
        subclases = SubClase.objects.all()
        return render(request, "productos/editar_producto.html", {"Producto":producto, "Subclases":subclases})

#Eliminar producto
def eliminar_producto(request, id):
    producto = Producto.objects.get(id=id)
    producto.delete()
    productos = Producto.objects.all()
    return render(request, "productos/productos.html", {"Productos":productos})
