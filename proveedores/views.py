from django.shortcuts import render
from django.http import HttpResponse
from planificador.models import Proveedor

#Mostrar proveedores
def proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, "proveedores/proveedores.html", {"Proveedores":proveedores})

"""
#Agregar proveedor
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
    nuevo_contacto = []
    nuevo_contacto.append(nombre_contacto)
    nuevo_contacto.append(correo)
    nuevo_contacto.append(telefono)
    #Lista calificaciones
    nombre_calificaciones = ["Precio","Tiempo Entrega","Calrutad"]
    calificaciones = [0,0,0]
    #Agregar proveedor
    nuevo_proveedor = Proveedor(rut=rut, nombre=nombre, clases=lista_clase, subclases=lista_subclase, lista_nombre_calificaciones=nombre_calificaciones, lista_calificaciones=calificaciones)
    nuevo_proveedor.lista_contactos.append(nuevo_contacto)
    nuevo_proveedor.save()
    proveedores = Proveedor.objects.all()
    return render(request, "proveedores/proveedores.html", {"Proveedores":proveedores})

#Vista proveedor
def proveedor(request, rut):
    proveedor = Proveedor.objects.get(rut=rut)
    if not proveedor.razon_social:
        razon_social = "No ingresado"
    else:
        razon_social = proveedor.razon_social
    calificacion_promedio = 0
    for calificacion in proveedor.lista_calificaciones:
        calificacion_promedio += calificacion
    calificacion_promedio = calificacion_promedio/len(proveedor.lista_calificaciones)
    lista_contactos = []
    for i in proveedor.lista_contactos:
        lista_contactos_aux = []
        contacto_split = i.split(",")
        lista_contactos_aux.append(contacto_split[0][2:-1])
        lista_contactos_aux.append(contacto_split[1][2:-1])
        lista_contactos_aux.append(contacto_split[2][2:-2])
        lista_contactos.append(lista_contactos_aux)
    return render(request, "proveedores/proveedor.html", {"Proveedor":proveedor, "razon_social":razon_social, "promedio":calificacion_promedio, "lista_contactos":lista_contactos})


#Edición proveedor
def mostrar_edicion_proveedor(request, rut):
    proveedor = Proveedor.objects.get(rut=rut)
    if request.method == "POST":
        proveedor.rut = request.POST["rut"]
        proveedor.nombre = request.POST["nombre"]
        clases = request.POST["clases"]
        sub_clase = request.POST["subclases"]
        proveedor.razon_social = request.POST["razon_social"]
        #Se añaden los datos a las listas
        lista_aux_contactos = []
        if clases:
            print(clases)
            lista_clase = clases.split(",")
            for i in lista_clase:
                print(i)
                proveedor.clases.append(i)
        if sub_clase:
            print(sub_clase)
            lista_subclase = sub_clase.split(",")
            for i in lista_subclase:
                print(i)
                proveedor.subclases.append(i)
        if request.POST["nombre1"]:
            lista_aux_contactos = []
            lista_aux_contactos.append(request.POST["nombre1"])
            lista_aux_contactos.append(request.POST["correo1"])
            lista_aux_contactos.append(request.POST["telefono1"])
            proveedor.lista_contactos.append(lista_aux_contactos)
        if request.POST["nombre2"]:
            lista_aux_contactos = []
            lista_aux_contactos.append(request.POST["nombre2"])
            lista_aux_contactos.append(request.POST["correo2"])
            lista_aux_contactos.append(request.POST["telefono2"])
            proveedor.lista_contactos.append(lista_aux_contactos)
        if request.POST["nombre3"]:
            lista_aux_contactos = []
            lista_aux_contactos.append(request.POST["nombre3"])
            lista_aux_contactos.append(request.POST["correo3"])
            lista_aux_contactos.append(request.POST["telefono3"])
            proveedor.lista_contactos.append(lista_aux_contactos)
        if request.POST["Precio"]:
            print(proveedor.lista_calificaciones[0])
            proveedor.lista_calificaciones[0] = (float(proveedor.lista_calificaciones[0])+float(request.POST["Precio"]))/2
            print(proveedor.lista_calificaciones[0])
        if request.POST["Tiempo"]:
            proveedor.lista_calificaciones[1] = (float(proveedor.lista_calificaciones[1])+float(request.POST["Tiempo"]))/2
        if request.POST["Calidad"]:
            proveedor.lista_calificaciones[2] = (float(proveedor.lista_calificaciones[2])+float(request.POST["Calidad"]))/2
        proveedor.save()
        proveedores = Proveedor.objects.all()
        return render(request, "proveedores/proveedores.html", {"Proveedores":proveedores})
    else:
        clases = str(proveedor.clases)
        lista_contactos = []
        for i in proveedor.lista_contactos:
            lista_contactos_aux = []
            contacto_split = i.split(",")
            lista_contactos_aux.append(contacto_split[0][2:-1])
            lista_contactos_aux.append(contacto_split[1][2:-1])
            lista_contactos_aux.append(contacto_split[2][2:-2])
            lista_contactos.append(lista_contactos_aux)
        return render(request, "proveedores/editar_proveedor.html", {"Proveedor":proveedor, "Clases":clases, "lista_contactos":lista_contactos})

#Eliminar proveedor
def eliminar_proveedor(request, rut):
    proveedor = Proveedor.objects.get(rut=rut)
    proveedor.delete()
    proveedores = Proveedor.objects.all()
    return render(request, "proveedores/proveedores.html", {"proveedores":proveedores})
"""