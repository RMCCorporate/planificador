from django.shortcuts import render
from django.http import HttpResponse
from planificador.models import Proveedor, Clase, SubClase, Contacto, Calificacion, Calificacion_Proveedor

#Mostrar proveedores
def proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, "proveedores/proveedores.html", {"Proveedores":proveedores})


#Agregar proveedor
def agregar_proveedor(request):
    clases = Clase.objects.all()
    subclases = []
    nombres = []
    for clase in clases:
        subclases_aux = []
        nombres.append(clase.nombre)
        for subclase in clase.subclases.all():
            subclases_aux.append(subclase)
        subclases.append(subclases_aux)
    #CAMBIAR CUANDO EXISTAN MÁS CLASES
    clase1 = subclases[0]
    clase2 = subclases[1]
    #clase3 = subclases[2]
    return render(request, "proveedores/crear_proveedor.html", {"clase1":clase1, "clase2":clase2, "nombre_1":nombres[0], "nombre_2":nombres[1]})#"clase3":clase3,  "nombre_3":nombres[2]})

def recibir_datos_proveedor(request):
    rut = request.GET["rut"]
    nombre = request.GET["nombre"]
    razon_social = request.GET["razon_social"]
    subclase = request.GET.getlist("subclase")
    #Contactos
    nombre_contacto = request.GET["nombre_contacto"]
    correo = request.GET["correo"]
    telefono = request.GET["telefono"]
    nuevo_contacto = Contacto(correo=correo, telefono=telefono, nombre=nombre_contacto)
    nuevo_contacto.save()
    #Agregar proveedor
    nuevo_proveedor = Proveedor(rut=rut, nombre=nombre, razon_social=razon_social)
    nuevo_proveedor.save()
    nuevo_proveedor.contactos_asociados.add(nuevo_contacto)
    for i in subclase:
        subclase = SubClase.objects.get(nombre=i)
        nuevo_proveedor.subclases_asociadas.add(subclase)
    precio_proveedor = Calificacion_Proveedor(rut, "Precio", 0)
    precio_proveedor.save()
    tiempo_respuesta_proveedor = Calificacion_Proveedor(rut, "Tiempo entrega", 0)
    tiempo_respuesta_proveedor.save()
    calidad_proveedor = Calificacion_Proveedor(rut, "Calidad", 0)
    calidad_proveedor.save()
    proveedores = Proveedor.objects.all()
    return render(request, "proveedores/proveedores.html", {"Proveedores":proveedores})

#Vista proveedor
def proveedor(request, rut):
    proveedor = Proveedor.objects.get(rut=rut)
    if not proveedor.razon_social:
        razon_social = "No ingresado"
    else:
        razon_social = proveedor.razon_social
    subclase = proveedor.subclases_asociadas.all()
    contactos = proveedor.contactos_asociados.all()
    calificaciones = Calificacion_Proveedor.objects.filter(proveedor=rut)
    promedio = 0
    suma_total = 0
    for i in calificaciones:
        suma_total += i.nota
    promedio = suma_total/len(calificaciones)
    return render(request, "proveedores/proveedor.html", {"Proveedor":proveedor, "subclase":subclase, "contactos":contactos, "calificaciones":calificaciones, "promedio":promedio})

"""
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