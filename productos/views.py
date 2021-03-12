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
    productos = Producto.objects.all()
    return render(request, "productos/productos.html", {"Productos":productos})
   
#Vista producto
def producto(request, id):
    producto = Producto.objects.get(id=id)
    print(producto.lista_precios)
    print(producto.fechas_actualizaciones_historicas)
    print(producto.lista_proveedores)
    print(producto.lista_tipo_cambio)
    lista_informacion_precios = []
    aux_informacion_precios = []
    for i,n in enumerate(producto.lista_precios):
        print(n)
        aux_informacion_precios = [n, producto.fechas_actualizaciones_historicas[i], producto.lista_proveedores[i], producto.lista_tipo_cambio[i]]
        lista_informacion_precios.append(aux_informacion_precios)
        print(lista_informacion_precios)
    return render(request, "productos/producto.html", {"Producto":producto, "Lista_precios":lista_informacion_precios})

#Edición producto
def mostrar_edicion_producto(request, id):
    producto = Producto.objects.get(id=id)
    if request.method == "POST":
        producto.id = request.POST["id"]
        producto.nombre = request.POST["nombre"]
        producto.clase = request.POST["clase"]
        producto.sub_clase = request.POST["subclase"]
        producto.unidad = request.POST["unidad"]
        nuevo_precio = request.POST["precio"]
        fecha_actualizacion = request.POST["fecha"]
        moneda = request.POST["moneda"]
        producto.ultimo_proveedor = request.POST["proveedor"]
        #Se añaden los datos a las listas
        producto.lista_precios.append(nuevo_precio)
        producto.fechas_actualizaciones_historicas.append(fecha_actualizacion)
        producto.lista_proveedores.append(producto.ultimo_proveedor)
        producto.lista_tipo_cambio.append(moneda)
        producto.save()
        productos = Producto.objects.all()
        return render(request, "productos/productos.html", {"Productos":productos})
    else:
        return render(request, "productos/editar_producto.html", {"Producto":producto})

#Eliminar producto
def eliminar_producto(request, id):
    producto = Producto.objects.get(id=id)
    producto.delete()
    productos = Producto.objects.all()
    return render(request, "productos/productos.html", {"Productos":productos})
