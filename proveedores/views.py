from django.shortcuts import render, redirect
from django.http import HttpResponse
from planificador.models import (
    Proveedor,
    Clase,
    SubClase,
    Contacto,
    Calificacion,
    Calificacion_Proveedor,
    User,
    Notificacion,
    Permisos_notificacion,
    Producto,
)
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from planificador.filters import ProveedoresFilter, Filtro_producto
from planificador.decorators import allowed_users
import openpyxl
import uuid

# FUNCIONES
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


def crear_notificacion(
    tipo,
    correo_usuario,
    accion,
    modelo_base_datos,
    numero_modificado,
    id_modelo,
    nombre,
):
    hora_actual = datetime.now()
    usuario = User.objects.get(correo=correo_usuario)
    permiso_notificacion = Permisos_notificacion.objects.get(nombre=tipo)
    notificacion = Notificacion(
        id=uuid.uuid1(),
        tipo=tipo,
        accion=accion,
        modelo_base_datos=modelo_base_datos,
        numero_modificado=numero_modificado,
        id_modelo=id_modelo,
        nombre=nombre,
        fecha=hora_actual,
    )
    notificacion.save()
    notificacion.usuario_modificacion = usuario
    notificacion.save()
    for i in permiso_notificacion.usuarios.all():
        i.notificaciones += 1
        i.save()
        if not notificacion.id_proyecto:
            texto_correo = "NOTIFICACIÓN: \nEstimado {} {}: \nEl usuario: {} {}, {} con detalle {} {} con fecha {}".format(
                i.nombre,
                i.apellido,
                notificacion.usuario_modificacion.nombre,
                notificacion.usuario_modificacion.apellido,
                notificacion.accion,
                notificacion.id_modelo,
                notificacion.nombre,
                notificacion.fecha,
            )
        else:
            texto_correo = "NOTIFICACIÓN: \nEstimado {} {}: \nEl usuario: {} {}, {} en el proyecto {} {} con fecha {}".format(
                i.nombre,
                i.apellido,
                notificacion.usuario_modificacion.nombre,
                notificacion.usuario_modificacion.apellido,
                notificacion.accion,
                notificacion.id_proyecto,
                notificacion.nombre,
                notificacion.fecha,
            )
        correo_enviador = "logistica@rmc.cl"
        clave_enviador = "RMC.1234"
        # CAMBIAR A i.correo
        correo_prueba = "tacorreahucke@gmail.com"
        mensaje = MIMEMultipart()
        mensaje["From"] = correo_enviador
        mensaje["To"] = correo_prueba
        mensaje["Subject"] = "NOTIFICACIÓN {}".format(notificacion.tipo)
        mensaje.attach(MIMEText(texto_correo, "plain"))
        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.starttls()
        session.login(correo_enviador, clave_enviador)
        text = mensaje.as_string()
        session.sendmail(correo_enviador, correo_prueba, text)
        session.quit()


# Mostrar proveedores
@login_required(login_url="/login")
def proveedores(request):
    proveedores = Proveedor.objects.all()
    myFilter = ProveedoresFilter(request.GET, queryset=proveedores)
    return render(
        request,
        "proveedores/proveedores.html",
        {"Proveedores": proveedores, "len": len(proveedores), "myFilter": myFilter},
    )


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
                    aux = []
                    aux.append(rut)
                    aux.append(nombre)
                    aux.append(row_data[3])
                    aux.append(contacto_correo)
                    aux.append("No se ingresó RUT, nombre proveedor o correo contacto")
                    datos_fallados.append(aux)
            else:
                if rut != "RUT":
                    if (
                        Contacto.objects.filter(correo=contacto_correo).exists()
                        or Proveedor.objects.filter(rut=rut).exists()
                    ):
                        aux = []
                        aux.append(rut)
                        aux.append(nombre)
                        aux.append(row_data[3])
                        aux.append(contacto_correo)
                        aux.append("El proveedor o correo del contacto ya existe")
                        datos_fallados.append(aux)
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
                                aux = []
                                aux.append(rut)
                                aux.append(nombre)
                                aux.append(row_data[3])
                                aux.append(contacto_correo)
                                aux.append(
                                    "El idioma tiene que ser 'ES', 'ESPAÑOL', 'EN', 'INGLÉS"
                                )
                                datos_fallados.append(aux)
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
                                aux = []
                                aux.append(rut)
                                aux.append(nombre)
                                aux.append(i)
                                aux.append(contacto_correo)
                                aux.append("No existe la subclase {}".format(i))
                                datos_fallados.append(aux)
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
        return render(
            request,
            "proveedores/resultado_planilla_proveedores.html",
            {"Fallo": datos_fallados, "Booleano": booleano_fallados},
        )
    else:
        return render(request, "proveedores/nuevo_proveedor_planilla.html")


# Agregar proveedor
@allowed_users(allowed_roles=["Admin", "Cotizador"])
@login_required(login_url="/login")
def agregar_proveedor(request):
    lista_clases = []
    clases = Clase.objects.all()
    for i in clases:
        aux = []
        aux.append(i)
        aux2 = []
        for n in i.subclases.all():
            aux2.append(n)
        aux.append(aux2)
        lista_clases.append(aux)
    return render(
        request, "proveedores/crear_proveedor.html", {"lista_clases": lista_clases}
    )


@login_required(login_url="/login")
def recibir_datos_proveedor(request):
    rut = str(request.GET["rut"])
    nombre = request.GET["nombre"]
    razon_social = request.GET["razon_social"]
    subclase = request.GET.getlist("subclase")
    # Contactos
    nombre_contacto = request.GET["nombre_contacto"]
    correo = request.GET["correo"]
    telefono = request.GET["telefono"]
    direccion = request.GET["direccion"]
    nuevo_contacto = Contacto(correo=correo, telefono=telefono, nombre=nombre_contacto)
    nuevo_contacto.save()
    # Agregar proveedor
    nuevo_proveedor = Proveedor(
        rut=rut, nombre=nombre, razon_social=razon_social, direccion=direccion
    )
    nuevo_proveedor.save()
    nuevo_proveedor.contactos_asociados.add(nuevo_contacto)
    for i in subclase:
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
    return redirect("/proveedores/proveedor/{}".format(rut))


# Vista proveedor
@login_required(login_url="/login")
def proveedor(request, rut):
    proveedor = Proveedor.objects.get(rut=rut)
    subclase = proveedor.subclases_asociadas.all()
    contactos = proveedor.contactos_asociados.all()
    calificaciones = Calificacion_Proveedor.objects.filter(proveedor=rut)
    promedio = 0
    suma_total = 0
    for i in calificaciones:
        suma_total += i.nota
    promedio = round(suma_total / len(calificaciones))
    diferencia = 5 - promedio
    lista_promedio = []
    for x in range(promedio):
        lista_promedio.append(x)
    lista_diferencia = []
    for i in range(diferencia):
        lista_diferencia.append(i)
    lista_productos = []
    for i in proveedor.productos_no.all():
        lista_productos.append(i)
    return render(
        request,
        "proveedores/proveedor.html",
        {
            "Proveedor": proveedor,
            "subclase": subclase,
            "contactos": contactos,
            "calificaciones": calificaciones,
            "promedio": lista_promedio,
            "diferencia": lista_diferencia,
            "productos": lista_productos,
        },
    )


# Edición proveedor
@allowed_users(allowed_roles=["Admin", "Cotizador"])
@login_required(login_url="/login")
def mostrar_edicion_proveedor(request, rut):
    proveedor = Proveedor.objects.get(rut=rut)
    if request.method == "POST":
        subclase = request.POST.getlist("subclase")
        # CONTACTO
        contacto = str(request.POST["contacto"])
        correo = request.POST["correo"]
        telefono = request.POST["telefono"]
        if correo != "":
            if Contacto.objects.filter(correo=correo).exists():
                nuevo_contacto = Contacto.objects.get(correo=correo)
                nuevo_contacto.nombre = contacto
                nuevo_contacto.telefono = telefono
                nuevo_contacto.save()
            else:
                nuevo_contacto = Contacto(
                    correo=correo, telefono=telefono, nombre=contacto
                )
                nuevo_contacto.save()
        # CALIFICACIONES
        calificaciones_precio = Calificacion_Proveedor.objects.filter(
            proveedor=rut, calificacion="Precio"
        )[0]
        calificaciones_precio.nota = (
            calificaciones_precio.nota + float(request.POST["Precio"])
        ) / 2
        calificaciones_precio.save()
        calificaciones_tiempo_entrega = Calificacion_Proveedor.objects.filter(
            proveedor=rut, calificacion="Tiempo entrega"
        )[0]
        calificaciones_tiempo_entrega.nota = (
            calificaciones_tiempo_entrega.nota + float(request.POST["Tiempo"])
        ) / 2
        calificaciones_tiempo_entrega.save()
        calificaciones_calidad = Calificacion_Proveedor.objects.filter(
            proveedor=rut, calificacion="Calidad"
        )[0]
        calificaciones_calidad.nota = (
            calificaciones_calidad.nota + float(request.POST["Calidad"])
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
        # GUARDAMOS NUEVO CONTACTO
        proveedor.save()
        if subclase != []:
            for i in subclase:
                subclase_agregar = SubClase.objects.get(nombre=i)
                proveedor.subclases_asociadas.add(subclase_agregar)
        if correo != "":
            proveedor.contactos_asociados.add(nuevo_contacto)
        eliminar = request.POST.getlist("eliminar")
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
        for i in clases:
            aux = []
            aux.append(i)
            aux2 = []
            for n in i.subclases.all():
                aux2.append(n)
            aux.append(aux2)
            lista_clases.append(aux)
        return render(
            request,
            "proveedores/editar_proveedor.html",
            {
                "Proveedor": proveedor,
                "Subclases": subclase,
                "Contactos": contactos,
                "Calificaciones": calificaciones,
                "lista_clases": lista_clases,
            },
        )


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
                    aux.append(x)
                    aux.append(i)
                    aux.append(i.clase_set.all()[0])
                if len(aux) != 0:
                    productos.append(aux)
        return render(
            request,
            "proveedores/agregar_productos_no_disponibles.html",
            {"Proveedor": proveedor, "productos": productos},
        )


# Eliminar proveedor
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
