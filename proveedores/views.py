from django.shortcuts import render
from django.http import HttpResponse
from planificador.models import Proveedor, Contacto

#Mostrar proveedores
def proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, "proveedores/proveedores.html", {"Proveedores":proveedores})


#Agregar producto
def agregar_proveedor(request):
    return render(request, "proveedores/crear_proveedor.html")

def recibir_datos_proveedor(request):
    rut = request.GET["rut"]
    nombre = request.GET["nombre"]
    clase = request.GET["clase"]
    lista_clase = clase.split(",")
    sub_clase = request.GET["sub_clase"]
    lista_subclase = sub_clase.split(",")
    #Contactos
    nombre_contacto = request.GET["nombre_contacto"]
    correo = request.GET["correo"]
    telefono = request.GET["telefono"]
    nuevo_proveedor = Proveedor(rut=rut, nombre=nombre, clases=lista_clase, subclases=lista_subclase)
    nuevo_proveedor.save()
    contacto = Contacto(correo_id=correo, nombre_contacto=nombre_contacto, telefono=telefono)
    contacto.save()
    contactos = Contacto.objects.all()
    print(contactos)
    for i in contactos:
        i.delete()
    print(contactos)
    contacto.proveedor.add(nuevo_proveedor)
    proveedores = Proveedor.objects.all()
    return render(request, "proveedores/proveedores.html", {"Proveedores":proveedores})
""""
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
"""""