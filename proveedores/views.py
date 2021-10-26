from django.shortcuts import render, redirect
from planificador.models import (
    Proveedor,
    Clase,
    SubClase,
    Contacto,
    Calificacion,
    Calificacion_Proveedor,
    Producto,
)
from django.contrib.auth.decorators import login_required
from planificador.filters import ProveedoresFilter
from planificador.decorators import allowed_users
import openpyxl
from planificador.notificaciones import crear_notificacion


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
    # CAMBIAR CUANDO EXISTAN MÁS CLASES
    clase1 = subclases[0]
    clase2 = subclases[1]
    clase3 = subclases[2]
    return [nombres, clase1, clase2, clase3, subclases]


# Mostrar proveedores
@login_required(login_url="/login")
def proveedores(request):
    proveedores = Proveedor.objects.all()
    myFilter = ProveedoresFilter(request.GET, queryset=proveedores)
    payload = {"Proveedores": proveedores, "len": len(proveedores), "myFilter": myFilter}
    return render(request, "proveedores/proveedores.html", payload)


def nuevo_proveedor_planilla(request):
    if request.method == "POST":
        datos_fallados = []
        booleano_fallados = False
        excel_file = request.FILES["excel_file"]
        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb["proveedor"]
        contador_creado = 0
        creado = False
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            rut = row_data[0].upper()
            nombre = row_data[1].upper()
            razon_social = row_data[2].upper()
            idioma = row_data[4].upper()
            contacto_correo = row_data[5].lower()
            contacto_nombre = row_data[6].upper()
            contacto_telefono = row_data[7].upper()
            direccion = row_data[8].upper()
            if (
                rut == "NONE"
                or nombre == "NONE"
                or contacto_correo == "NONE"
                or row_data[3] == "None"
            ):
                if not (
                    rut == "NONE"
                    or nombre == "NONE"
                    or contacto_correo == "NONE"
                    or row_data[3] == "None"
                    and contacto_nombre == "NONE"
                    and contacto_telefono == "NONE"
                    and direccion == "NONE"
                ):
                    datos_fallados.append([rut, nombre, row_data[3], contacto_correo,
                                          "No se ingresó RUT, nombre proveedor o correo contacto"])
            else:
                if rut != "RUT":
                    if (
                        Contacto.objects.filter(correo=contacto_correo).exists()
                        or Proveedor.objects.filter(rut=rut).exists()
                    ):
                        datos_fallados.append([rut, nombre, row_data[3], contacto_correo,
                                              "El proveedor o correo del contacto ya existe"])
                    else:
                        nuevo_proveedor = Proveedor(rut=rut, nombre=nombre)
                        if row_data[2] != "None":
                            nuevo_proveedor.razon_social = razon_social
                        if idioma != "NONE":
                            if (
                                idioma == "ES"
                                or idioma == "ESPAÑOL"
                                or idioma == "EN"
                                or idioma == "INGLES"
                                or idioma == "INGLÉS"
                            ):
                                nuevo_proveedor.idioma = idioma
                            else:
                                datos_fallados.append([rut, nombre, row_data[3], contacto_correo,
                                                      "El idioma tiene que ser 'ES', 'ESPAÑOL', 'EN', 'INGLÉS"])
                        if direccion != "NONE":
                            nuevo_proveedor.direccion = direccion
                        nuevo_proveedor.save()
                        subclases = row_data[3]
                        subclases_repartidas = subclases.split(",")
                        for i in subclases_repartidas:
                            subclase = i.upper()
                            if SubClase.objects.filter(nombre=subclase).exists():
                                dato_subclase = SubClase.objects.get(nombre=subclase)
                                nuevo_proveedor.subclases_asociadas.add(dato_subclase)
                            else:
                                datos_fallados.append([rut, nombre, i, contacto_correo,
                                                      "No existe la subclase {}".format(i)])
                        if contacto_correo != "none":
                            nuevo_contacto = Contacto(correo=contacto_correo)
                            if contacto_nombre != "NONE":
                                nuevo_contacto.nombre = contacto_nombre
                            if contacto_telefono != "NONE":
                                nuevo_contacto.telefono = contacto_telefono
                            nuevo_contacto.save()
                            nuevo_proveedor.contactos_asociados.add(nuevo_contacto)
                        if Calificacion.objects.filter(
                            nombre="Tiempo_entrega"
                        ).exists():
                            calificacion_tiempo_entrega = Calificacion.objects.get(
                                nombre="Tiempo entrega"
                            )
                        else:
                            calificacion_tiempo_entrega = Calificacion(
                                nombre="Tiempo entrega",
                                descripción="Define el tiempo de entrega por parte del proveedor",
                            )
                            calificacion_tiempo_entrega.save()
                        if Calificacion.objects.filter(nombre="Precio").exists():
                            calificacion_precio = Calificacion.objects.get(
                                nombre="Precio"
                            )
                        else:
                            calificacion_precio = Calificacion(
                                nombre="Precio", descripción="Define qué tan barato es"
                            )
                            calificacion_precio.save()
                        if Calificacion.objects.filter(nombre="Calidad").exists():
                            calificacion_calidad = Calificacion.objects.get(
                                nombre="Calidad"
                            )
                        else:
                            calificacion_calidad = Calificacion(
                                nombre="Calidad",
                                descripción="Define la calidad de los productos",
                            )
                            calificacion_calidad.save()
                        calificacion_provedor_tiempo_entrega = Calificacion_Proveedor(
                            proveedor=nuevo_proveedor,
                            calificacion=calificacion_tiempo_entrega,
                            nota=0,
                        )
                        calificacion_provedor_tiempo_entrega.save()
                        calificacion_provedor_precio = Calificacion_Proveedor(
                            proveedor=nuevo_proveedor,
                            calificacion=calificacion_precio,
                            nota=0,
                        )
                        calificacion_provedor_precio.save()
                        calificacion_provedor_calidad = Calificacion_Proveedor(
                            proveedor=nuevo_proveedor,
                            calificacion=calificacion_calidad,
                            nota=0,
                        )
                        calificacion_provedor_calidad.save()
                        nuevo_proveedor.save()
                        contador_creado += 1
                        creado = True
        if creado:
            crear_notificacion(
                "agregar_proveedor",
                request.user.email,
                "creó proveedor(es) mediante planilla",
                "Proveedor",
                contador_creado,
                " ",
                " ",
            )
        if len(datos_fallados) != 0:
            booleano_fallados = True
        payload = {"Fallo": datos_fallados, "Booleano": booleano_fallados}
        return render(request, "proveedores/resultado_planilla_proveedores.html", payload)
    else:
        return render(request, "proveedores/nuevo_proveedor_planilla.html")


# Agregar proveedor
@allowed_users(allowed_roles=["Admin", "Cotizador"])
@login_required(login_url="/login")
def agregar_proveedor(request):
    clases = Clase.objects.all()
    lista_clases = [(i, [n for n in i.subclases.all()]) for i in clases]
    payload = {"lista_clases": lista_clases}
    return render(request, "proveedores/crear_proveedor.html", payload)


@login_required(login_url="/login")
def recibir_datos_proveedor(request):
    get = request.get
    nombre_contacto = get["nombre_contacto"]
    nuevo_contacto = Contacto(correo=get["correo"], telefono=get["telefono"], nombre=nombre_contacto)
    nuevo_contacto.save()
    nuevo_proveedor = Proveedor(
        rut=str(get["rut"]), nombre=get["nombre"], razon_social=get["razon_social"], direccion=get["direccion"]
    )
    nuevo_proveedor.save()
    nuevo_proveedor.contactos_asociados.add(nuevo_contacto)
    for i in get.getlist("subclase"):
        subclase = SubClase.objects.get(nombre=i)
        nuevo_proveedor.subclases_asociadas.add(subclase)
    precio = Calificacion.objects.get(nombre="Precio")
    precio_proveedor = Calificacion_Proveedor(
        proveedor=nuevo_proveedor, calificacion=precio, nota=0
    )
    precio_proveedor.save()
    tiempo_entrega = Calificacion.objects.get(nombre="Tiempo entrega")
    tiempo_respuesta_proveedor = Calificacion_Proveedor(
        proveedor=nuevo_proveedor, calificacion=tiempo_entrega, nota=0
    )
    tiempo_respuesta_proveedor.save()
    calidad = Calificacion.objects.get(nombre="Calidad")
    calidad_proveedor = Calificacion_Proveedor(
        proveedor=nuevo_proveedor, calificacion=calidad, nota=0
    )
    calidad_proveedor.save()
    crear_notificacion(
        "agregar_proveedor",
        request.user.email,
        "creó proveedor",
        "Proveedor",
        1,
        nuevo_proveedor.rut,
        nuevo_proveedor.nombre,
    )
    return redirect("/proveedores/proveedor/{}".format(str(get["rut"])))


# Vista proveedor
@login_required(login_url="/login")
def proveedor(request, rut):
    proveedor = Proveedor.objects.get(rut=rut)
    subclase = proveedor.subclases_asociadas.all()
    contactos = proveedor.contactos_asociados.all()
    calificaciones = Calificacion_Proveedor.objects.filter(proveedor=rut)
    promedio = 0
    suma_total = 0
    if calificaciones:
        for i in calificaciones:
            suma_total += i.nota
        promedio = round(suma_total / len(calificaciones))
    diferencia = 5 - promedio
    lista_promedio = [x for x in range(promedio)]
    lista_diferencia = [i for i in range(diferencia)]
    lista_productos = [i for i in proveedor.productos_no.all()]
    payload = {
        "Proveedor": proveedor,
        "subclase": subclase,
        "contactos": contactos,
        "calificaciones": calificaciones,
        "promedio": lista_promedio,
        "diferencia": lista_diferencia,
        "productos": lista_productos,
    }
    return render(request, "proveedores/proveedor.html", payload)


# Edición proveedor
@allowed_users(allowed_roles=["Admin", "Cotizador"])
@login_required(login_url="/login")
def mostrar_edicion_proveedor(request, rut):
    proveedor = Proveedor.objects.get(rut=rut)
    if request.method == "POST":
        post = request.POST
        if post["correo"] != "":
            if Contacto.objects.filter(correo=post["correo"]).exists():
                nuevo_contacto = Contacto.objects.get(correo=post["correo"])
                nuevo_contacto.nombre = str(post["contacto"])
                nuevo_contacto.telefono = post["telefono"]
                nuevo_contacto.save()
            else:
                nuevo_contacto = Contacto(
                    correo=post["correo"], telefono=post["telefono"], nombre=str(post["contacto"])
                )
                nuevo_contacto.save()
        calificaciones_precio = Calificacion_Proveedor.objects.filter(
            proveedor=rut, calificacion="Precio"
        )[0]
        calificaciones_precio.nota = (
            calificaciones_precio.nota + float(post["Precio"])
        ) / 2
        calificaciones_precio.save()
        calificaciones_tiempo_entrega = Calificacion_Proveedor.objects.filter(
            proveedor=rut, calificacion="Tiempo entrega"
        )[0]
        calificaciones_tiempo_entrega.nota = (
            calificaciones_tiempo_entrega.nota + float(post["Tiempo"])
        ) / 2
        calificaciones_tiempo_entrega.save()
        calificaciones_calidad = Calificacion_Proveedor.objects.filter(
            proveedor=rut, calificacion="Calidad"
        )[0]
        calificaciones_calidad.nota = (
            calificaciones_calidad.nota + float(post["Calidad"])
        ) / 2
        calificaciones_calidad.save()
        crear_notificacion(
            "editar_proveedor",
            request.user.email,
            "editó proveedor",
            "Proveedor",
            1,
            proveedor.rut,
            proveedor.nombre,
        )
        proveedor.save()
        if post.getlist("subclase") != []:
            for i in post.getlist("subclase"):
                subclase_agregar = SubClase.objects.get(nombre=i)
                proveedor.subclases_asociadas.add(subclase_agregar)
        if post["correo"] != "":
            proveedor.contactos_asociados.add(nuevo_contacto)
        eliminar = post.getlist("eliminar")
        for i in eliminar:
            if i != "No":
                contacto_eliminar = Contacto.objects.get(correo=i)
                crear_notificacion(
                    "eliminar_contacto",
                    request.user.email,
                    "eliminó contacto",
                    "Proveedor",
                    1,
                    contacto_eliminar.correo,
                    contacto_eliminar.nombre,
                )
                contacto_eliminar.delete()
        return redirect("/proveedores/proveedor/{}".format(proveedor.rut))
    else:
        subclase = proveedor.subclases_asociadas.all()
        contactos = proveedor.contactos_asociados.all()
        calificaciones = Calificacion_Proveedor.objects.filter(proveedor=rut)
        lista_clases = []
        clases = Clase.objects.all()
        lista_clases = [(i, [n for n in i.subclases.all()]) for i in clases]
        payload = {
            "Proveedor": proveedor,
            "Subclases": subclase,
            "Contactos": contactos,
            "Calificaciones": calificaciones,
            "lista_clases": lista_clases,
        }
        return render(request, "proveedores/editar_proveedor.html", payload)


# Edición proveedor
@allowed_users(allowed_roles=["Admin", "Cotizador"])
@login_required(login_url="/login")
def agregar_productos_no_disponibles(request, rut):
    proveedor = Proveedor.objects.get(rut=rut)
    if request.method == "POST":
        productos = request.POST.getlist("eliminar")
        for i in productos:
            producto = Producto.objects.get(id=i)
            proveedor.productos_no.add(producto)
            proveedor.save()
        return redirect("/proveedores/proveedor/{}".format(proveedor.rut))
    else:
        productos = []
        subclase = proveedor.subclases_asociadas.all()
        for i in subclase:
            productos_de_subclase = i.productos.all()
            for x in productos_de_subclase:
                aux = []
                no_existe_producto = False
                for n in proveedor.productos_no.all():
                    if x.id == n.id:
                        no_existe_producto = True
                if not no_existe_producto:
                    aux = [x, i, i.clase_set.all()[0]]
                    productos.append(aux)
        payload = {"Proveedor": proveedor, "productos": productos}
        return render(request, "proveedores/agregar_productos_no_disponibles.html", payload)


@allowed_users(allowed_roles=["Admin", "Cotizador"])
@login_required(login_url="/login")
def eliminar_proveedor(request, rut):
    proveedor = Proveedor.objects.get(rut=rut)
    for i in proveedor.contactos_asociados.all():
        i.delete()
    crear_notificacion(
        "eliminar_proveedor",
        request.user.email,
        "eliminó proveedor",
        "Proveedor",
        1,
        proveedor.rut,
        proveedor.nombre,
    )
    proveedor.delete()
    return redirect("/proveedores")
