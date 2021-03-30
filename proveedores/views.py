from django.shortcuts import render
from django.http import HttpResponse
from planificador.models import Proveedor, Clase, SubClase, Contacto, Calificacion, Calificacion_Proveedor
import openpyxl

#FUNCIONES
def mostrar_clases():
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
    clase3 = subclases[2]
    return [nombres, clase1, clase2, clase3]

#Mostrar proveedores
def proveedores(request):
    proveedores = Proveedor.objects.all()
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb["proveedor"]
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            if row_data[0] != "rut":
                nuevo_proveedor = Proveedor(rut=row_data[0], nombre=row_data[1], razon_social=row_data[2], idioma=row_data[4])
                nuevo_proveedor.save()
                subclases = row_data[3]
                subclases_repartidas = subclases.split(',')
                for i in subclases_repartidas:
                    subclase = SubClase.objects.get(nombre=i)
                    nuevo_proveedor.subclases_asociadas.add(subclase)
                nuevo_contacto = Contacto(correo=row_data[5], telefono=row_data[7], nombre=row_data[6])
                nuevo_contacto.save()
                nuevo_proveedor.contactos_asociados.add(nuevo_contacto)
                calificacion_tiempo_entrega = Calificacion.objects.get(nombre="Tiempo entrega")
                calificacion_precio = Calificacion.objects.get(nombre="Precio")
                calificacion_calidad = Calificacion.objects.get(nombre="Calidad")
                calificacion_provedor_tiempo_entrega = Calificacion_Proveedor(proveedor=nuevo_proveedor, calificacion=calificacion_tiempo_entrega, nota=0)
                calificacion_provedor_tiempo_entrega.save()
                calificacion_provedor_precio = Calificacion_Proveedor(proveedor=nuevo_proveedor, calificacion=calificacion_precio, nota=0)
                calificacion_provedor_precio.save()
                calificacion_provedor_calidad = Calificacion_Proveedor(proveedor=nuevo_proveedor, calificacion=calificacion_calidad, nota=0)
                calificacion_provedor_calidad.save()
    return render(request, "proveedores/proveedores.html", {"Proveedores":proveedores})

#Agregar proveedor
def agregar_proveedor(request):
    clases = Clase.objects.all()
    lista_clases = mostrar_clases()
    return render(request, "proveedores/crear_proveedor.html", {"clase1":lista_clases[1], "clase2":lista_clases[2], "nombre_1":lista_clases[0][0], "nombre_2":lista_clases[0][1], "clase3":lista_clases[3],  "nombre_3":lista_clases[0][2]})

def recibir_datos_proveedor(request):
    rut = str(request.GET["rut"])
    nombre = request.GET["nombre"]
    razon_social = request.GET["razon_social"]
    subclase = request.GET.getlist("subclase")
    #Contactos
    nombre_contacto = request.GET["nombre_contacto"]
    correo = request.GET["correo"]
    telefono = request.GET["telefono"]
    direccion = request.GET["direccion"]
    nuevo_contacto = Contacto(correo=correo, telefono=telefono, nombre=nombre_contacto)
    nuevo_contacto.save()
    #Agregar proveedor
    nuevo_proveedor = Proveedor(rut=rut, nombre=nombre, razon_social=razon_social, direccion=direccion)
    nuevo_proveedor.save()
    nuevo_proveedor.contactos_asociados.add(nuevo_contacto)
    for i in subclase:
        subclase = SubClase.objects.get(nombre=i)
        nuevo_proveedor.subclases_asociadas.add(subclase)
    precio = Calificacion.objects.get(nombre="Precio")
    precio_proveedor = Calificacion_Proveedor(proveedor=nuevo_proveedor, calificacion=precio, nota=0)
    precio_proveedor.save()
    tiempo_entrega = Calificacion.objects.get(nombre="Tiempo entrega")
    tiempo_respuesta_proveedor = Calificacion_Proveedor(proveedor=nuevo_proveedor, calificacion=tiempo_entrega, nota=0)
    tiempo_respuesta_proveedor.save()
    calidad = Calificacion.objects.get(nombre="Calidad")
    calidad_proveedor = Calificacion_Proveedor(proveedor=nuevo_proveedor, calificacion=calidad, nota=0)
    calidad_proveedor.save()
    proveedores = Proveedor.objects.all()
    return render(request, "proveedores/proveedores.html", {"Proveedores":proveedores})

#Vista proveedor
def proveedor(request, rut):
    proveedor = Proveedor.objects.get(rut=rut)
    subclase = proveedor.subclases_asociadas.all()
    contactos = proveedor.contactos_asociados.all()
    calificaciones = Calificacion_Proveedor.objects.filter(proveedor=rut)
    promedio = 0
    suma_total = 0
    for i in calificaciones:
        suma_total += i.nota
    promedio = suma_total/len(calificaciones)
    return render(request, "proveedores/proveedor.html", {"Proveedor":proveedor, "subclase":subclase, "contactos":contactos, "calificaciones":calificaciones, "promedio":promedio})


#Edición proveedor
def mostrar_edicion_proveedor(request, rut):
    proveedor = Proveedor.objects.get(rut=rut)
    if request.method == "POST":
        subclase = request.POST.getlist("subclase")
        #CONTACTO
        contacto = str(request.POST["contacto"])
        correo = request.POST["correo"]
        telefono = request.POST["telefono"]
        if correo != "":
            nuevo_contacto = Contacto(correo=correo, telefono=telefono, nombre=contacto)
            nuevo_contacto.save()
        #CALIFICACIONES
        calificaciones_precio = Calificacion_Proveedor.objects.filter(proveedor=rut, calificacion="Precio")[0]
        calificaciones_precio.nota = (calificaciones_precio.nota+float(request.POST["Precio"]))/2
        calificaciones_precio.save()
        calificaciones_tiempo_entrega = Calificacion_Proveedor.objects.filter(proveedor=rut, calificacion="Tiempo entrega")[0]
        calificaciones_tiempo_entrega.nota = (calificaciones_tiempo_entrega.nota+float(request.POST["Tiempo"]))/2
        calificaciones_tiempo_entrega.save()
        calificaciones_calidad = Calificacion_Proveedor.objects.filter(proveedor=rut, calificacion="Calidad")[0]
        calificaciones_calidad.nota = (calificaciones_calidad.nota+float(request.POST["Calidad"]))/2
        calificaciones_calidad.save()
        #GUARDAMOS NUEVO CONTACTO
        proveedor.save()
        if subclase != []:
            for i in subclase:
                subclase_agregar = SubClase.objects.get(nombre=i)
                proveedor.subclases_asociadas.add(subclase_agregar)
        if correo != "":
            proveedor.contactos_asociados.add(nuevo_contacto)
        proveedores = Proveedor.objects.all()
        return render(request, "proveedores/proveedores.html", {"Proveedores":proveedores})
    else:
        subclase = proveedor.subclases_asociadas.all()
        contactos = proveedor.contactos_asociados.all()
        calificaciones = Calificacion_Proveedor.objects.filter(proveedor=rut)
        lista_clases = mostrar_clases()
        return render(request, "proveedores/editar_proveedor.html", {"Proveedor":proveedor, "Subclases":subclase, "Contactos":contactos, "Calificaciones":calificaciones, "clase1":lista_clases[1], "clase2":lista_clases[2], "nombre_1":lista_clases[0][0], "nombre_2":lista_clases[0][1], "clase3":lista_clases[3], "nombre_3":lista_clases[0][2]})

#Eliminar proveedor
def eliminar_proveedor(request, rut):
    proveedor = Proveedor.objects.get(rut=rut)
    proveedor.delete()
    proveedores = Proveedor.objects.all()
    return render(request, "proveedores/proveedores.html", {"proveedores":proveedores})
""