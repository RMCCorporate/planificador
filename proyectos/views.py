from black import re
from django.shortcuts import render, redirect
from planificador.models import (
    SubClase,
    Producto,
    Proveedor,
    Contacto,
    Proyecto,
    Producto_proyecto,
    Precio,
    Filtro_producto,
    Cotizacion,
    Producto_proveedor,
    Correlativo_cotizacion,
    Orden_compra,
    RMC,
    Presupuesto_subclases,
    Producto_proyecto_cantidades,
    Importaciones,
    InstalacionProyecto
)
from planificador.filters import (
    Filtro_productoFilter,
    ProyectosFilter,
)
from django.contrib.auth.decorators import login_required
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date, datetime
from planificador.decorators import allowed_users
import uuid
from operator import itemgetter
from RMC_Corporate.settings import EXCEL_ROOT
from django.contrib.auth import get_user_model
from planificador.notificaciones import texto_en_html, crear_notificacion


lista_producto_general = []


def clases_lista_productos(clase):
    sub_clase_general = []
    for i in clase:
        subclase_aux = []
        subclase_aux.append([i.nombre])
        productos_aux = []
        for producto in i.productos.all():
            productos_aux.append(producto)
        subclase_aux.append(productos_aux)
        sub_clase_general.append(subclase_aux)
    return sub_clase_general


def crear_correo(usuario, cotizacion, texto_extra, clave, subject):
    texto_html = texto_en_html(usuario)
    texto_correo = ""
    texto_lista_productos = ""
    for i in cotizacion.productos_asociados.all():
        producto_proyecto = Producto_proyecto.objects.get(
            producto=cotizacion.proyecto_asociado, proyecto=i
        )
        nombre = i.nombre
        if Producto_proveedor.objects.filter(
            proyecto=i, producto=cotizacion.proveedor_asociado
        ).exists():
            nombre = Producto_proveedor.objects.get(
                proyecto=i, producto=cotizacion.proveedor_asociado
            ).nombre_proveedor
        texto_lista_productos += "\n- {}: {} {}\n".format(
            nombre, producto_proyecto.cantidades, i.unidad
        )
    for i in cotizacion.contacto_asociado.all():
        texto_español = (
            "Estimado {}, \nSe solicita cotización de: \n{} \n{}\nSaludos.".format(
                i.nombre, texto_lista_productos, texto_extra
            )
        )
        texto_ingles = "Dear {}, \nA quote is requested for: \n{} \n{}\nRegards.".format(
            i.nombre, texto_lista_productos, texto_extra
        )
        if cotizacion.proveedor_asociado.idioma == "ESP":
            texto_correo = texto_español
        else:
            texto_correo = texto_ingles
        # CAMBIAR A LOGISTICA
        correo_enviador = usuario.correo
        clave_enviador = clave
        # CAMBIAR A "i.correo"
        correo_prueba = "tacorrea@uc.cl"
        mensaje = MIMEMultipart()
        mensaje["From"] = correo_enviador
        mensaje["To"] = correo_prueba
        mensaje["Subject"] = subject
        mensaje.attach(MIMEText(texto_correo, "plain"))
        mensaje.attach(MIMEText(texto_html, "html"))
        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.starttls()
        session.login(correo_enviador, clave_enviador)
        text = mensaje.as_string()
        session.sendmail(correo_enviador, correo_prueba, text)
        session.quit()
    for i in cotizacion.productos_asociados.all():
        producto_proyecto = Producto_proyecto.objects.get(
            producto=cotizacion.proyecto_asociado, proyecto=i
        )
        producto_proyecto.estado_cotizacion = "Enviada"


@login_required(login_url="/login")
def proyectos(request):
    proyectos = Proyecto.objects.all()
    myFilter = ProyectosFilter(request.GET, queryset=proyectos)
    payload = {"Proyectos": proyectos, "len": len(proyectos), "myFilter": myFilter}
    return render(request, "proyectos/proyectos.html", payload)


@login_required(login_url="/login")
def proyecto(request, id):
    usuario = str(request.user.groups.all()[0])
    proyecto = Proyecto.objects.get(id=id)
    productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
    cotizaciones = Cotizacion.objects.filter(proyecto_asociado=proyecto)
    precio_final = 0
    lista_productos_precio = []
    tabla_productos = []
    for i in productos_proyecto:
        precio = list(i.proyecto.lista_precios.all()).pop() if len(i.proyecto.lista_precios.all()) != 0 else "No"
        tabla_productos.append([i, precio])
    tabla_cotizaciones = []
    tabla_productos_cotizados = []
    for i in cotizaciones:
        for producto in i.productos_asociados.all():
            if producto.lista_precios:
                precios = producto.lista_precios.all()
                if precios.filter(
                    nombre_cotizacion=i.nombre,
                    nombre_proveedor=i.proveedor_asociado.nombre,
                ).exists():
                    precio = list(
                        precios.filter(
                            nombre_cotizacion=i.nombre,
                            nombre_proveedor=i.proveedor_asociado.nombre,
                        )
                    ).pop()
                    tabla_productos_cotizados.append([producto, precio])
                else:
                    precio = ""
        estado = ""
        if i.fecha_respuesta:
            demora_respuesta = i.fecha_respuesta - i.fecha_salida
            if demora_respuesta.days > 10:
                estado = "Rojo"
            elif 10 >= demora_respuesta.days > 5:
                estado = "Naranjo"
            elif 5 >= demora_respuesta.days:
                estado = "Verde"
        else:
            demora_respuesta = date.today() - i.fecha_salida
            if demora_respuesta.days > 10:
                estado = "Rojo"
            elif 10 >= demora_respuesta.days > 5:
                estado = "Naranjo"
            elif 5 >= demora_respuesta.days:
                estado = "Verde"
            demora_respuesta = None
        if i.fecha_actualizacion_precio and i.fecha_respuesta:
            demora_precio = i.fecha_actualizacion_precio - i.fecha_respuesta
        else:
            demora_precio = ""
        tabla_cotizaciones.append(i, [Producto_proyecto.objects.get(proyecto=producto, producto=proyecto)],
                                  [demora_respuesta, demora_precio, estado])
    lista_precio = list(dict.fromkeys(lista_productos_precio))
    if len(lista_precio) == len(productos_proyecto):
        proyecto.estado = "Completo"
        proyecto.save()
    else:
        proyecto.estado = "Incompleto"
        proyecto.save()
    for i in productos_proyecto:
        precios = i.proyecto.lista_precios.all()
        if len(precios) != 0:
            a = list(precios).pop()
            ultimo_precio = a.valor
            if a.valor_cambio:
                ultimo_precio = a.valor * a.valor_cambio
            ultimo_precio = ultimo_precio * i.cantidades if i.cantidades else 0
            if a.valor_importación:
                ultimo_precio += a.valor_importación * a.valor_cambio
            precio_final += ultimo_precio
        if i.fecha_uso:
            if 10 < (i.fecha_uso - date.today()).days:
                i.estado_tiempo = "Verde"
                i.save()
            elif 10 >= (i.fecha_uso - date.today()).days > 5:
                i.estado_tiempo = "Naranjo"
                i.save()
            elif 5 >= (i.fecha_uso - date.today()).days:
                i.estado_tiempo = "Rojo"
                i.save()
            else:
                i.estado_tiempo = "No"
                i.save()
    utilidad_subclase = 0
    for i in proyecto.presupuesto_subclases.all():
        if i.utilidad:
            utilidad_subclase += i.valor * (1 + (i.utilidad / 100))
    diccionario_hh1 = {"hh1":0, "hh2":0, "hh3":0, "hh4":0, "hh5":0, "hh6":0, "hh7":0, "hh8":0}
    for x in productos_proyecto:
        if x.proyecto.hh1:
            diccionario_hh1["hh1"] += x.proyecto.hh1
        if x.proyecto.hh2:
            diccionario_hh1["hh2"] += x.proyecto.hh2
        if x.proyecto.hh3:
            diccionario_hh1["hh3"] += x.proyecto.hh3
        if x.proyecto.hh4:
            diccionario_hh1["hh4"] += x.proyecto.hh4
        if x.proyecto.hh5:
            diccionario_hh1["hh5"] += x.proyecto.hh5
        if x.proyecto.hh6:
            diccionario_hh1["hh6"] += x.proyecto.hh6
        if x.proyecto.hh7:
            diccionario_hh1["hh7"] += x.proyecto.hh7
        if x.proyecto.hh8:
            diccionario_hh1["hh7"] += x.proyecto.hh8
        
    payload = {
        "Proyecto": proyecto,
        "Productos": tabla_productos,
        "cotizaciones": tabla_cotizaciones,
        "info_productos": tabla_productos_cotizados,
        "precio": precio_final,
        "rol": usuario,
        "utilidad_subclase": utilidad_subclase,
        "hh1": diccionario_hh1
    }
    return render(request, "proyectos/proyecto.html", payload)


@allowed_users(allowed_roles=["Admin", "Cotizador"])
@login_required(login_url="/login")
def editar_precios(request, id):
    if request.method == "POST":
        post = request.POST
        cotizacion = Cotizacion.objects.get(id=id)
        if request.user.nombre:
            usuario_modificacion = request.user.nombre + " " + request.user.apellido
        else:
            usuario_modificacion = ""
        fecha_actual = date.today()
        for n, producto in enumerate(post.getlist("id_producto")):
            producto = Producto.objects.get(id=producto)
            producto_proyecto = Producto_proyecto.objects.get(
                producto=cotizacion.proyecto_asociado, proyecto=producto
            )
            nuevo_valor_importacion = 0 if not post.getlist("valor_importacion")[n] else post.getlist("valor_importacion")[n]
            nuevo_tipo_cambio = "CLP" if not post.getlist("tipo_cambio")[n] else post.getlist("tipo_cambio")[n]
            nuevo_valor_cambio = 1 if not post.getlist("tipo_cambio")[n] else post.getlist("tipo_cambio")[n]
            precio = Precio(
                id=uuid.uuid1(),
                valor=post.getlist("valor")[n],
                valor_importación=nuevo_valor_importacion,
                fecha=fecha_actual,
                tipo_cambio=nuevo_tipo_cambio,
                valor_cambio=nuevo_valor_cambio,
                nombre_proveedor=cotizacion.proveedor_asociado.nombre,
                nombre_cotizacion=cotizacion.nombre,
                usuario_modificacion=usuario_modificacion,
            )
            precio.save()
            cotizacion.fecha_actualizacion_precio = datetime.now()
            cotizacion.save()
            usuario = get_user_model().objects.get(correo=request.user.correo)
            usuario.precios.add(precio)
            usuario.save()
            producto_proyecto.estado_cotizacion = "Precio"
            producto_proyecto.save()
            producto.lista_precios.add(precio)
            producto.save()
            producto_proyecto.estado_cotizacion = "Precio"
            producto_proyecto.save()
        for i in post.getlist("fecha"):
            cotizacion.fecha_respuesta = i
            cotizacion.save()
        """
        crear_notificacion(
            "editar_precio",
            request.user.correo,
            "editó precio",
            "Precio y Cotización",
            len(post.getlist("id_producto")),
            cotizacion.proyecto_asociado.id,
            cotizacion.proyecto_asociado.nombre,
        )
        """
        
        return redirect(
            "/proyectos/proyecto/{}".format(cotizacion.proyecto_asociado.id)
        )
    else:
        cotizacion = Cotizacion.objects.get(id=id)
        lista_productos = []
        productos = cotizacion.productos_asociados.all()
        for i in productos:
            auxiliar_lista_productos = []
            auxiliar_lista_productos.append(i)
            precios = i.lista_precios.all()
            if precios.filter(nombre_cotizacion=cotizacion.nombre).exists():
                auxiliar_lista_productos.append(
                    precios.filter(nombre_cotizacion=cotizacion.nombre)
                )
            else:
                auxiliar_lista_productos.append([])
            lista_productos.append(auxiliar_lista_productos)
        payload = {"info_productos": lista_productos, "Cotizacion": cotizacion}
        return render(request, "proyectos/editar_precio.html", payload)


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def editar_datos_producto_proyecto(request, id):
    if request.method == "POST":
        post = request.POST
        proyecto = Proyecto.objects.get(id=id)
        if request.user.nombre:
            usuario_modificacion = request.user.nombre + " " + request.user.apellido
        else:
            usuario_modificacion = ""
        cotizaciones = Cotizacion.objects.filter(proyecto_asociado=proyecto)
        status = []
        for i in post.getlist("id"):
            if post[str(i)] != "no_hay":
                status.append(post[str(i)])
            else:
                status.append(" ")
        for n, i in enumerate(post.getlist("nombre")):
            producto = Producto.objects.get(nombre=i)
            producto_proyecto = Producto_proyecto.objects.get(
                producto=proyecto, proyecto=producto
            )
            producto_proyecto.cantidades = float(post.getlist("cantidades")[n])
            producto_proyecto.status = status[n]
            if post.getlist("fecha_uso")[n] != "None" and post.getlist("fecha_uso")[n] != "":
                producto_proyecto.fecha_uso = post.getlist("fecha_uso")[n]
            producto_proyecto.usuario_modificacion = usuario_modificacion
            producto_proyecto.save()
            usuario = get_user_model().objects.get(correo=request.user.correo)
            usuario.productos_proyecto.add(producto_proyecto)
            usuario.save()
        """
        crear_notificacion(
            "editar_producto_proyecto",
            request.user.correo,
            "editó información de producto proyecto",
            "Producto_proyecto",
            len(post.getlist("nombre")),
            proyecto.id,
            proyecto.nombre,
        )
        """
        
        eliminar = post.getlist("eliminar")
        if eliminar:
            for i in eliminar:
                producto_eliminar = Producto_proyecto.objects.get(id=i)
                for i in cotizaciones:
                    for n in i.productos_asociados.all():
                        if n.nombre == producto_eliminar.proyecto.nombre:
                            i.productos_asociados.remove(n)
                producto_eliminar.delete()
                usuario = get_user_model().objects.get(correo=request.user.correo)
                usuario.productos_proyecto.remove(producto_eliminar)
            crear_notificacion(
                "eliminar_producto_proyecto",
                request.user.correo,
                "eliminó producto proyecto",
                "Producto_proyecto",
                len(eliminar),
                proyecto.id,
                proyecto.nombre,
            )
        return redirect("/proyectos/proyecto/{}".format(proyecto.id))
    else:
        proyecto = Proyecto.objects.get(id=id)
        productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
        lista_info_productos = []
        for i in productos_proyecto:
            producto = Producto.objects.get(nombre=i.proyecto)
            ultimo_precio = list(producto.lista_precios.all())
            if len(ultimo_precio) != 0:
                ultimo_precio = ultimo_precio.pop()
            lista_info_productos.append([i, ultimo_precio])
        payload = {"info_productos": lista_info_productos}
        return render(request, "proyectos/editar_producto_proyecto.html", payload)


@login_required(login_url="/login")
def editar_fechas(request, id):
    proyecto = Proyecto.objects.get(id=id)
    if request.method == "POST":
        proyecto.fecha_inicio = request.POST["fecha_inicio"]
        proyecto.fecha_final = request.POST["fecha_termino"]
        proyecto.save()
        return redirect("/proyectos/proyecto/{}".format(proyecto.id))
    else:
        return render(request, "proyectos/editar_fechas.html", {"Proyecto": proyecto})


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def agregar_producto(request, id):
    if request.method == "GET":
        if request.path_info == "/agregar_producto/lista_productos_agregar":
            get = request.GET
            id = get["id"]
            instancia_proyecto = Proyecto.objects.get(id=id)
            productos = get.getlist("productos_checkeados")
            lista_productos = []
            if productos:
                for i in productos:
                    aux = []
                    instancia_producto = Producto.objects.get(nombre=i)
                    sub_clase = instancia_producto.subclase_set.all()[0]
                    aux.append(instancia_producto)
                    aux.append(sub_clase)
                    if Producto_proyecto.objects.filter(
                        producto=instancia_proyecto, proyecto=instancia_producto
                    ).exists():
                        aux.append(
                            Producto_proyecto.objects.get(
                                producto=instancia_proyecto, proyecto=instancia_producto
                            )
                        )
                    lista_productos.append(aux)
                if Proveedor.objects.filter(subclases_asociadas=sub_clase).exists():
                    proveedores = Proveedor.objects.filter(
                        subclases_asociadas=sub_clase
                    )
                payload = {"Proyecto": instancia_proyecto,
                           "Producto": lista_productos,
                           "Proveedores": proveedores}
                return render(request, "proyectos/crear_producto_proyecto.html", payload)
            else:
                error = "No se ingresó ningún producto."
                return render(request, "error_general.html", {"error": error})
        else:
            get = request.GET
            if id == "guardar_datos_filtro_agregar_proyecto":
                id = get["id"]
            proyecto = Proyecto.objects.get(id=id)
            nuevo_productos_proyecto = Producto_proyecto.objects.filter(
                producto=proyecto
            )
            productos = Filtro_producto.objects.all()
            myFilter = Filtro_productoFilter(get, queryset=productos)
            lista_productos = []
            payload = {
                "id": id,
                "Proyecto": proyecto,
                "myFilter": myFilter,
                "productos_proyecto": nuevo_productos_proyecto,
            }
            return render(request, "proyectos/agregar_producto.html", payload)
    elif request.method == "POST":
        get = request.GET
        post = request.POST
        if request.user.nombre:
            usuario_modificacion = request.user.nombre + " " + request.user.apellido
        else:
            usuario_modificacion = ""
        proyecto = Proyecto.objects.get(id=post["id"])
        productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
        for i in post.getlist("producto"):
            booleano_repeticion = False
            for n in productos_proyecto:
                if n.proyecto.nombre == i:
                    booleano_repeticion = True
            if not booleano_repeticion and i:
                producto = Producto.objects.get(nombre=i)
                nuevo_producto_proyecto = Producto_proyecto(
                    id=uuid.uuid1(),
                    producto=proyecto,
                    proyecto=producto,
                    usuario_modificacion=usuario_modificacion,
                    estado_cotizacion="No",
                )
                nuevo_producto_proyecto.save()
        productos = Filtro_producto.objects.all()
        myFilter = Filtro_productoFilter(get, queryset=productos)
        producto = myFilter.qs
        nuevo_productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
        payload = {"id": post["id"],
                   "Proyecto": proyecto,
                   "myFilter": myFilter,
                   "productos_proyecto": nuevo_productos_proyecto
                   }
        return render(request, "proyectos/agregar_producto.html", payload)


@login_required(login_url="/login")
def crear_nuevo_producto(request):
    if request.user.nombre:
        usuario_modificacion = request.user.nombre + " " + request.user.apellido
    else:
        usuario_modificacion = ""
    post = request.POST
    proyecto = Proyecto.objects.get(id=post["id_proyecto"])
    cantidades = post.getlist("cantidades")
    for n, i in enumerate(post.getlist("id_producto")):
        status = post[i]
        producto = Producto.objects.get(id=i)
        cantidades[n] = 0 if cantidades[n] == "" else cantidades[n]
        if not Producto_proyecto.objects.filter(
            producto=proyecto, proyecto=producto
        ).exists():
            nuevo_producto_proyecto = Producto_proyecto(
                id=uuid.uuid1(),
                producto=proyecto,
                proyecto=producto,
                status=status,
                fecha_uso=post.getlist("fecha_uso")[n],
                cantidades=cantidades[n],
                usuario_modificacion=usuario_modificacion,
                estado_cotizacion="No",
            )
            nuevo_producto_proyecto.save()
            usuario = get_user_model().objects.get(correo=request.user.correo)
            usuario.productos_proyecto.add(nuevo_producto_proyecto)
            usuario.save()
        else:
            producto_proyecto = Producto_proyecto.objects.get(
                producto=proyecto, proyecto=producto
            )
            producto_proyecto.status = status
            producto_proyecto.fecha_uso = post.getlist("fecha_uso")[n]
            producto_proyecto.cantidades = cantidades[n]
            producto_proyecto.usuario_modificacion = usuario_modificacion
            producto_proyecto.save()
        if post.getlist("fecha_uso")[n] != "":
            producto_proyecto.fecha_uso = post.getlist("fecha_uso")[n]
        subclase_producto = producto.subclase_set.all()[0]
        if not proyecto.presupuesto_subclases.filter(
            subclase=subclase_producto
        ).exists():
            nuevo_presupuesto_subclase = Presupuesto_subclases(
                id=uuid.uuid1(), valor=0, subclase=subclase_producto
            )
            nuevo_presupuesto_subclase.save()
            proyecto.presupuesto_subclases.add(nuevo_presupuesto_subclase)
            proyecto.save()
    """
    crear_notificacion(
        "agregar_producto_proyecto",
        request.user.correo,
        "creó producto(s) en proyecto",
        "Producto_Proyecto",
        len(post.getlist("id_producto")),
        proyecto.id,
        proyecto.nombre,
    )
    """
    
    return redirect("/proyectos/proyecto/{}".format(proyecto.id))


@login_required(login_url="/login")
def planificador(request):
    usuario = str(request.user)
    if (
        usuario == "tacorrea@uc.cl"
        or usuario == "pcorrea"
        or usuario == "rcasascordero"
        or usuario == "vvergara"
        or usuario == "tacorrea"
    ):
        return render(request, "proyectos/planificador.html")
    else:
        return redirect("/")


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def mostrar_filtro(request):
    get = request.GET
    centro_costos = get["centro_costos"]
    if get["edicion"] == "No" and Proyecto.objects.filter(id=centro_costos).exists():
        return render(request, "proyectos/planificador.html", {"error": "ERROR"})
    else:
        valor_cambio = 0 if not get["valor_cambio"] else get["valor_cambio"]
        tipo_cambio = "CLP" if not get["tipo_cambio"] else get["tipo_cambio"]
        if request.user.nombre:
            creador = request.user.nombre + " " + request.user.apellido
        else:
            creador = ""
        fecha_actual = datetime.now()
        nuevo_proyecto = Proyecto(id=get["centro_costos"],
                                  nombre=get["nombre"],
                                  precio_final=0,
                                  fecha_creacion=fecha_actual,
                                  tipo_cambio=tipo_cambio,
                                  valor_cambio=valor_cambio,
                                  creador=creador,
                                  consolidacion=False)
        nuevo_proyecto.save()
        if get["fecha_inicio"]:
            nuevo_proyecto.fecha_inicio = get["fecha_inicio"]
        if get["fecha_termino"]:
            nuevo_proyecto.fecha_final = get["fecha_termino"]
        nuevo_proyecto.save()
        """
        crear_notificacion(
            "crear_proyecto",
            request.user.correo,
            "creó un proyecto",
            "Proyecto",
            1,
            get["centro_costos"],
            get["nombre"],
        )
        """
        productos = Filtro_producto.objects.all()
        productos_proyecto = nuevo_proyecto.productos.all()
        myFilter = Filtro_productoFilter(get, queryset=productos)
        payload = {
            "Proyecto": nuevo_proyecto,
            "myFilter": myFilter,
            "productos_proyecto": productos_proyecto,
        }
        return render(request, "proyectos/eleccion_productos.html", payload)


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def guardar_datos_filtro(request):
    get = request.GET
    if request.user.nombre:
        usuario_modificacion = request.user.nombre + " " + request.user.apellido
    else:
        usuario_modificacion = ""
    proyecto = Proyecto.objects.get(id=get["centro_costos"])
    productos_proyecto_anterior = proyecto.productos.all()
    diccionario_productos = {}
    for i in get.getlist("productos"):
        diccionario_productos[i] = False
        if len(productos_proyecto_anterior) != 0:
            for x in productos_proyecto_anterior:
                if x.nombre == i:
                    diccionario_productos[i] = True
    if len(diccionario_productos) != 0:
        for i in diccionario_productos.keys():
            if not diccionario_productos[i]:
                producto = Producto.objects.get(nombre=i)
                if not Producto_proyecto.objects.filter(producto=proyecto, proyecto=producto).exists():
                    nuevo_producto_proyecto = Producto_proyecto(
                        id=uuid.uuid1(),
                        producto=proyecto,
                        proyecto=producto,
                        usuario_modificacion=usuario_modificacion,
                        estado_cotizacion="No",
                    )
                    nuevo_producto_proyecto.save()
                    if producto.proveedor_interno:
                        proveedor_int = Proveedor.objects.get(nombre=producto.proveedor_interno)
                        nuevo_producto_proyecto.proveedores.add(proveedor_int)
                        nuevo_producto_proyecto.save()
                    proyecto.save()
                    usuario = get_user_model().objects.get(correo=request.user.correo)
                    usuario.proyectos.add(proyecto)
                    usuario.save()
    productos_proyecto = proyecto.productos.all()
    productos = Filtro_producto.objects.all()
    for i in productos_proyecto:
        if productos.filter(nombre_producto=i):
            s = productos.filter(nombre_producto=i)[0]
            s.utilizado = proyecto.id
            s.save()
    myFilter = Filtro_productoFilter(get, queryset=productos)
    payload = {"Proyecto": proyecto,
               "myFilter": myFilter,
               "productos_proyecto": productos_proyecto}
    return render(request, "proyectos/eleccion_productos.html", payload)


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def recibir_datos_planificador(request):
    get = request.GET
    proyecto = Proyecto.objects.get(id=request.GET["centro_costos"])
    productos = list(dict.fromkeys(get.getlist("productos_checkeados")))
    lista_subclases_productos = []
    for producto in productos:
        lista_aux_producto = []
        producto_clase = Producto.objects.get(nombre=producto)
        lista_aux_producto.append(producto_clase)
        if Producto_proyecto.objects.filter(producto=proyecto, proyecto=producto_clase):
            lista_aux_producto.append(
                Producto_proyecto.objects.filter(
                    producto=proyecto, proyecto=producto_clase
                )[0]
            )
        lista_subclases_productos.append(lista_aux_producto)
    payload = {"Proyecto": proyecto, "Productos": lista_subclases_productos}
    return render(request, "proyectos/lista_productos.html", payload)


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def recibir_cantidades_planificador(request):
    proyecto = Proyecto.objects.get(id=request.GET["centro_costos"])
    cantidad = request.GET.getlist("cantidad")
    productos = request.GET.getlist("id_producto")
    boton = request.GET["boton"]
    for counter, i in enumerate(productos):
        nuevo_producto = Producto.objects.get(nombre=i)
        producto_proyecto = Producto_proyecto.objects.get(
            producto=proyecto, proyecto=nuevo_producto
        )
        if cantidad[counter]:
            producto_proyecto.cantidades = float(cantidad[counter])
        else:
            producto_proyecto.cantidades = 0
        producto_proyecto.save()
        usuario = get_user_model().objects.get(correo=request.user.correo)
        usuario.productos_proyecto.add(producto_proyecto)
        usuario.save()
    if boton == "GUARDAR Y CONTINUAR":
        productos = Filtro_producto.objects.all()
        myFilter = Filtro_productoFilter(request.GET, queryset=productos)
        productos_proyecto = proyecto.productos.all()
        payload = {"Proyecto": proyecto,
                   "myFilter": myFilter,
                   "productos_proyecto": productos_proyecto}
        return render(request, "proyectos/eleccion_productos.html", payload)
    else:
        for i in proyecto.productos.all():
            subclase = i.subclase_set.all()[0].nombre
            lista_subclases_final = list(dict.fromkeys([subclase]))
        aux = []
        for i in lista_subclases_final:
            instancia_subclase = SubClase.objects.get(nombre=i)
            lista_con_utilidad = [i, instancia_subclase.utilidad] if instancia_subclase.utilidad else [i, 0]
            aux.append(lista_con_utilidad)
        payload = {"Proyecto": proyecto, "subclases": aux}
        return render(request, "proyectos/eleccion_presupuesto.html", payload)


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def eleccion_presupuesto(request, id):
    post = request.POST
    proyecto = Proyecto.objects.get(id=id)
    proyecto.presupuesto_total = post["presupuesto_total"]
    proyecto.save()
    for n, i in enumerate(post.getlist("subclases")):
        modelo_subclase = SubClase.objects.get(nombre=post.getlist("subclases_nombres")[n])
        nuevo_presupuesto_subclase = Presupuesto_subclases(
            id=uuid.uuid1(), valor=i, subclase=modelo_subclase, utilidad=post.getlist("utilidad")[n]
        )
        nuevo_presupuesto_subclase.save()
        proyecto.presupuesto_subclases.add(nuevo_presupuesto_subclase)
        proyecto.save()
    return redirect("/proyectos/proyecto/{}".format(proyecto.id))


@allowed_users(allowed_roles=["Admin", "Cotizador"])
@login_required(login_url="/login")
def agregar_cotizacion(request, id):
    if request.method == "POST":
        post = request.POST
        proyecto_asociado = Proyecto.objects.get(id=id)
        if request.user.nombre:
            usuario_modificacion = request.user.nombre + " " + request.user.apellido
        else:
            usuario_modificacion = ""
        diccionario_proveedores = {}
        for i in post.getlist("contacto"):
            producto, proveedor, contacto = i.split("**")
            if proveedor not in diccionario_proveedores.keys():
                diccionario_proveedores[proveedor] = [[contacto], [producto]]
            else:
                diccionario_proveedores[proveedor][0].append(contacto)
                diccionario_proveedores[proveedor][1].append(producto)
        año_hoy = datetime.now().year
        if Correlativo_cotizacion.objects.filter(año=año_hoy).exists():
            correlativo = Correlativo_cotizacion.objects.get(año=año_hoy)
            correlativo.numero += 1
            correlativo.save()
        else:
            correlativo = Correlativo_cotizacion(año=año_hoy, numero=0)
            correlativo.save()
        nombre_con_correlativo = post["nombre"] + " - " + "0" * (4 - len(str(correlativo.numero))) + str(correlativo.numero)
        for nombre_proveedor in diccionario_proveedores:
            proveedor = Proveedor.objects.get(nombre=nombre_proveedor)
            nueva_cotizacion = Cotizacion(
                id=uuid.uuid1(),
                nombre=nombre_con_correlativo,
                proyecto_asociado=proyecto_asociado,
                proveedor_asociado=proveedor,
                fecha_salida=datetime.now(),
                usuario_modificacion=usuario_modificacion,
            )
            nueva_cotizacion.save()
            usuario = get_user_model().objects.get(correo=str(request.user.correo))
            usuario.cotizaciones.add(nueva_cotizacion)
            usuario.save()
            for id in diccionario_proveedores[nombre_proveedor][1]:
                nuevo_producto = Producto.objects.get(id=id)
                nuevo_producto_proyecto = Producto_proyecto.objects.get(
                    producto=proyecto_asociado, proyecto=nuevo_producto
                )
                nueva_cotizacion.productos_asociados.add(nuevo_producto)
                nueva_cotizacion.save()
                nuevo_producto_proyecto.estado_cotizacion = "Creada"
                nuevo_producto_proyecto.save()
            contactos_sin_repetir = list(
                dict.fromkeys(diccionario_proveedores[nombre_proveedor][0])
            )
            for contactos in contactos_sin_repetir:
                contacto_agregar = Contacto.objects.get(nombre=contactos)
                nueva_cotizacion.contacto_asociado.add(contacto_agregar)
                nueva_cotizacion.save()
        """
        crear_notificacion(
            "crear_cotizacion",
            request.user.correo,
            "creó cotizaciones",
            "Cotización",
            1,
            nueva_cotizacion.id,
            nueva_cotizacion.nombre,
        )
        """
        return redirect("/proyectos/proyecto/{}".format(proyecto_asociado.id))
    else:
        proyecto = Proyecto.objects.get(id=id)
        productos = proyecto.productos.all()
        lista_productos = []
        for i in productos:
            lista_producto_proyecto = []
            lista_proveedores = []
            producto_proyecto = Producto_proyecto.objects.filter(
                producto=proyecto, proyecto=i
            )
            lista_producto_proyecto.append(producto_proyecto[0])
            proveedores = Proveedor.objects.filter(
                subclases_asociadas=producto_proyecto[0].proyecto.subclase_set.all()[0]
            )
            for n in proveedores:
                for contacto in n.contactos_asociados.all():
                    no_existe = True if n.productos_no.all().filter(id=producto_proyecto[0].proyecto.id).exists() else False
                    if not no_existe:
                        lista_proveedores.append([n, contacto])
            lista_producto_proyecto.append(lista_proveedores)
            lista_productos.append(lista_producto_proyecto)
        payload = {"Proyecto": proyecto, "Proveedores": lista_productos}
        return render(request, "proyectos/crear_cotizacion.html", payload)


@login_required(login_url="/login")
def mostrar_cotizacion(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    productos = [Producto_proyecto.objects.get(producto=cotizacion.proyecto_asociado, proyecto=i)
                 for i in cotizacion.productos_asociados.all()]
    contactos = cotizacion.contacto_asociado.all()
    orden_compra = Orden_compra.objects.get(cotizacion_hija=cotizacion) if cotizacion.orden_compra else False
    productos_orden_compra = cotizacion.productos_proyecto_asociados.all() if cotizacion.orden_compra else False
    payload = {
        "Cotizacion": cotizacion,
        "Productos": productos,
        "contactos": contactos,
        "orden_compra": orden_compra,
        "productos_orden_compra": productos_orden_compra,
        "EXCEL_ROOT": EXCEL_ROOT,
    }
    return render(request, "proyectos/cotizacion.html", payload)


@allowed_users(allowed_roles=["Admin", "Cotizador"])
@login_required(login_url="/login")
def editar_cotizacion(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    if request.method == "POST":
        if request.user.nombre:
            usuario_modificacion = request.user.nombre + " " + request.user.apellido
        else:
            usuario_modificacion = ""
        cotizacion.nombre = request.POST["nombre"]
        cotizacion.usuario_modificacion = usuario_modificacion
        cotizacion.fecha_respuesta = request.POST["fecha_respuesta"]
        cotizacion.save()
        usuario = get_user_model().objects.get(correo=request.user.correo)
        usuario.cotizaciones.add(cotizacion)
        usuario.save()
        """
        crear_notificacion(
            "editar_fecha_respuesta_cotización",
            request.user.correo,
            "editó cotización",
            "Cotización",
            1,
            cotizacion.id,
            cotizacion.nombre,
        )
        """
        return redirect("/proyectos/mostrar_cotizacion/{}".format(cotizacion.id))
    else:
        return render(
            request, "proyectos/editar_cotizacion.html", {"Cotizacion": cotizacion}
        )


@allowed_users(allowed_roles=["Admin", "Cotizador"])
@login_required(login_url="/login")
def editar_disponibilidad(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    if request.method == "POST":
        proveedor = cotizacion.proveedor_asociado
        for i in request.POST.getlist("producto"):
            producto = Producto.objects.get(id=i)
            proveedor.productos_no.add(producto)
            proveedor.save()
        return redirect("/proyectos/mostrar_cotizacion/{}".format(cotizacion.id))
    else:
        productos_asociados = cotizacion.productos_asociados.all()
        payload = {"Cotizacion": cotizacion, "info_productos": productos_asociados}
        return render(request, "proyectos/editar_disponibilidad.html", payload)


@allowed_users(allowed_roles=["Admin", "Cotizador"])
@login_required(login_url="/login")
def eliminar_cotizacion(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    proyecto = cotizacion.proyecto_asociado.id
    """
    crear_notificacion(
        "eliminar_cotización",
        request.user.correo,
        "eliminó cotización",
        "Cotización",
        1,
        cotizacion.id,
        cotizacion.nombre,
    )
    """
    cotizacion.delete()
    return redirect("/proyectos/proyecto/{}".format(proyecto))


@login_required(login_url="/login")
def enviar_correo(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    proyecto = cotizacion.proyecto_asociado.id
    if request.method == "POST":
        post = request.POST
        usuario = get_user_model().objects.get(correo=request.user.correo)
        crear_correo(usuario, cotizacion, request.POST["texto"], post["clave"], post["subject"])
        cotizacion.fecha_salida = datetime.now()
        cotizacion.save()
        """
        crear_notificacion(
            "enviar_correo",
            request.user.correo,
            "envió correo con cotización",
            "Cotización",
            1,
            cotizacion.id,
            cotizacion.nombre,
        )
        """
        
        return redirect("/proyectos/proyecto/{}".format(proyecto))
    else:
        contacto = cotizacion.contacto_asociado.all()
        payload = {"Cotizacion": cotizacion, "contactos": contacto}
        return render(request, "proyectos/enviar_correo.html", payload)


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def informar_orden_compra(request, id):
    proyecto = Proyecto.objects.get(id=id)
    if request.method == "POST":
        post = request.POST
        cotizador = get_user_model().objects.filter(email=post["enviar"])
        productos_cantidades = []
        cantidad_orden_compra = []
        for i in post.getlist("nombre"):
            nuevo = i.split("*")
            cantidad_orden_compra.append(nuevo[1])
            productos_cantidades.append([nuevo[0], nuevo[1], post[nuevo[2]]])
        numero_orden_compra = len(list(dict.fromkeys(cantidad_orden_compra)))
        usuario_cotizador = get_user_model().objects.get(correo=post["enviar"])
        if not usuario_cotizador.orden_compra:
            usuario_cotizador.orden_compra = 0
            usuario_cotizador.save()
        usuario_cotizador.orden_compra += numero_orden_compra
        usuario_cotizador.save()
        planificadores = get_user_model().objects.filter(groups__name="Planificador")
        for i in planificadores:
            usuario_planificador = get_user_model().objects.get(correo=i.email)
            if not usuario_planificador.orden_compra:
                usuario_planificador.orden_compra = 0
                usuario_planificador.save()
            usuario_planificador.orden_compra += numero_orden_compra
            usuario_planificador.save()
        texto_correo = ""
        texto_lista_productos = ""
        texto_entrada = "{} {},\nSe adjunta información para realización de órdenes de compra: \n(Nº Cotización, nombre producto, cantidad) \n\n".format(
            cotizador[0].nombre, cotizador[0].apellido
        )
        lista_ordenada = sorted(productos_cantidades, key=itemgetter(1))
        for producto in lista_ordenada:
            texto_productos = "{} - {} - {} \n".format(
                producto[1], producto[0], producto[2]
            )
            texto_lista_productos += texto_productos
        texto_correo += texto_entrada
        texto_correo += texto_lista_productos
        texto_correo += "\nObservaciones: {}\n".format(post["observaciones"])
        texto_correo += "Facturar a: {} \n".format(post["empresa"])
        # CAMBIAR A LOGISTICA
        correo_enviador = "tcorrea@rmc.cl"
        clave_enviador = "Tom12345"
        # CAMBIAR A "i.correo"
        correo_prueba = "tacorrea@uc.cl"
        mensaje = MIMEMultipart()
        mensaje["From"] = correo_enviador
        mensaje["To"] = correo_prueba
        mensaje["Subject"] = "Crear orden de compra"
        mensaje.attach(MIMEText(texto_correo, "plain"))
        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.starttls()
        session.login(correo_enviador, clave_enviador)
        text = mensaje.as_string()
        session.sendmail(correo_enviador, correo_prueba, text)
        session.quit()
        return redirect("/proyectos/proyecto/{}".format(id))
    else:
        cotizaciones = Cotizacion.objects.filter(proyecto_asociado=proyecto)
        tabla_productos_cotizados = []
        for i in cotizaciones:
            for producto in i.productos_asociados.all():
                if producto.lista_precios:
                    precios = producto.lista_precios.all()
                    if precios.filter(nombre_cotizacion=i.nombre,
                                      nombre_proveedor=i.proveedor_asociado.nombre).exists():
                        precio = list(precios.filter(nombre_cotizacion=i.nombre,
                                                     nombre_proveedor=i.proveedor_asociado.nombre)).pop()
                        tabla_productos_cotizados.append([Producto_proyecto.objects.get(proyecto=producto, producto=proyecto), precio])
                    else:
                        precio = ""
        cotizadores = get_user_model().objects.filter(groups__name="Cotizador")
        payload = {"productos": tabla_productos_cotizados, "cotizadores": cotizadores}
        return render(request, "proyectos/informar_orden_compra.html", payload)


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def editar_presupuesto(request, id):
    proyecto = Proyecto.objects.get(id=id)
    if request.method == "POST":
        post = request.POST
        proyecto.presupuesto_total = float(post["presupuesto_total"])
        proyecto.save()
        for n, i in enumerate(post.getlist("subclases")):
            for x in proyecto.presupuesto_subclases.all():
                if x.subclase.nombre == post.getlist("subclases_nombres")[n]:
                    subclase_encontrada = SubClase.objects.get(nombre=x.subclase.nombre)
                    subclase_final = proyecto.presupuesto_subclases.filter(
                        subclase=subclase_encontrada
                    )[0]
                    subclase_final.valor = float(i)
                    subclase_final.utilidad = float(post.getlist("utilidad")[n])
                    subclase_final.save()
        return redirect("/proyectos/proyecto/{}".format(id))
    else:
        presupuesto_subclases = proyecto.presupuesto_subclases.all()
        payload = {"Proyecto": proyecto, "presupuesto_subclases": presupuesto_subclases}
        return render(request, "proyectos/editar_presupuesto.html", payload)


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def consolidar_proyecto(request, id):
    proyecto = Proyecto.objects.get(id=id)
    proyecto.consolidacion = True
    proyecto.save()
    return redirect("/proyectos/proyecto/{}".format(id))


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def agregar_orden_interna(request, id):
    proyecto = Proyecto.objects.get(id=id)
    if request.method == "POST":
        post = request.POST
        if request.user.nombre:
            usuario_modificacion = request.user.nombre + " " + request.user.apellido
        else:
            usuario_modificacion = ""
        proveedor = Proveedor.objects.get(rut=post["empresa"])
        lista_proveedor = {}
        for x in post.getlist("id_producto"):
            producto = Producto_proyecto.objects.get(id=x)
            info_precio_cantidad = post.getlist(x)
            if proveedor not in lista_proveedor.keys():
                lista_proveedor[info_precio_cantidad[0]] = [[producto, info_precio_cantidad[1], info_precio_cantidad[2]]]
            else:
                lista_proveedor[info_precio_cantidad[0]].append([producto, info_precio_cantidad[1], info_precio_cantidad[2]])
        for i in lista_proveedor.keys():
            proveedor_asociado = Proveedor.objects.get(nombre=i)
            nueva_cotizacion = Cotizacion(
                id=uuid.uuid1(),
                nombre=post["nombre"],
                proyecto_asociado=proyecto,
                orden_compra=True,
                proveedor_asociado=proveedor_asociado,
                fecha_salida=datetime.now(),
                fecha_respuesta=datetime.now(),
                fecha_actualizacion_precio=datetime.now(),
                usuario_modificacion=usuario_modificacion,
            )
            nueva_cotizacion.save()
            for n in lista_proveedor[i]:
                precio_asociado = Precio(
                    id=uuid.uuid1(),
                    valor=n[2],
                    fecha=datetime.now(),
                    nombre_proveedor=i,
                    nombre_cotizacion=nueva_cotizacion.nombre,
                    usuario_modificacion=usuario_modificacion,
                )
                precio_asociado.save()
                nuevo_producto_cantidades = Producto_proyecto_cantidades(
                    id=uuid.uuid1(),
                    proyecto_asociado_cantidades=proyecto,
                    producto_asociado_cantidades=n[0],
                    precio=precio_asociado,
                    cantidades=n[1],
                )
                nuevo_producto_cantidades.save()
                nueva_cotizacion.productos_asociados.add(n[0].proyecto)
                nueva_cotizacion.productos_proyecto_asociados.add(
                    nuevo_producto_cantidades
                )
                nueva_cotizacion.save()
            nombre_rmc = RMC.objects.get(rut=post["empresa"])
            nueva_orden_compra = Orden_compra(
                id=uuid.uuid1(),
                cotizacion_padre=nueva_cotizacion,
                cotizacion_hija=nueva_cotizacion,
                condicion_entrega="Inmediato",
                condiciones_pago=post["condicion_pago"],
                forma_pago="Interno",
                destino_factura=nombre_rmc,
                observaciones=post["observaciones"],
            )
            nueva_orden_compra.save()
        return redirect("/proyectos/proyecto/{}".format(id))
    else:
        lista_productos = []
        nombre_RMCs = [
            "INGENIERÍA Y SERVICIOS RMC LIMITADA",
            "RMC INDUSTRIAL SPA",
            "RMC EQUIPMENTS SPA",
            "RMC CORPORATE SPA",
            "RMC LABS SPA",
        ]
        productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
        for i in productos_proyecto:
            aux = []
            booleano = False
            for n in i.proveedores.all():
                if n.nombre in nombre_RMCs:
                    booleano = True
            if booleano:
                aux.append(i)
                for x in i.proveedores.all():
                    if x.nombre in nombre_RMCs:
                        aux.append(x.nombre)
                for y in i.proyecto.lista_precios.all():
                    if y.nombre_proveedor == aux[1]:
                        aux.append(y)
                    else:
                        aux.append("No hay")
                lista_productos.append(aux)
        payload = {"Proyecto": proyecto, "productos": lista_productos}
        return render(request, "proyectos/agregar_orden_interna.html", payload)


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def nueva_importacion(request, id):
    if request.method == "GET":
        if request.path_info == "/nueva_importacion/recibir_importacion":
            proyecto = Proyecto.objects.get(id=request.GET["centro_costos"])
            importacion = Importaciones.objects.get(codigo=request.GET["eleccion"])
            productos = importacion.productos.all()
            payload = {
                "Importacion": importacion,
                "Productos": productos,
                "Proyecto": proyecto,
            }
            return render(request, "proyectos/elegir_cantidades_importacion.html", payload)
        else:
            proyecto = Proyecto.objects.get(id=id)
            importaciones = Importaciones.objects.all()
            lista_importaciones = [i for i in importaciones]
            payload = {"importaciones": lista_importaciones, "Proyecto": proyecto}
            return render(request, "proyectos/nueva_importacion.html", payload)
    else:
        post = request.POST
        if request.user.nombre:
            usuario_modificacion = request.user.nombre + " " + request.user.apellido
        else:
            usuario_modificacion = ""
        proyecto = Proyecto.objects.get(id=post["centro_costos"])
        importacion = Importaciones.objects.get(codigo=post["importacion"])
        importaciones = Importaciones.objects.filter(
            codigo_referencial=importacion.codigo_referencial
        )
        importacion_antigua = False
        for i in importaciones:
            if i != importacion:
                importacion_antigua = i
        lista_con_cantidades = []
        for n, i in enumerate(post.getlist("eleccion")):
            for x in post.getlist("id_producto"):
                if i == x:
                    producto = Producto_proyecto_cantidades.objects.get(id=x)
                    lista_con_cantidades.append([producto, post.getlist("cantidad")[n]])
        if Cotizacion.objects.filter(
            nombre="Importacion{}".format(importacion.codigo_referencial)
        ).exists():
            nueva_cotizacion = Cotizacion.objects.get(
                nombre="Importacion{}".format(importacion.codigo_referencial)
            )
        else:
            nueva_cotizacion = Cotizacion(id=uuid.uuid1(),
                                          nombre="Importacion" + importacion.codigo_referencial,
                                          proyecto_asociado=proyecto,
                                          orden_compra=True,
                                          fecha_salida=datetime.now(),
                                          fecha_respuesta=datetime.now(),
                                          fecha_actualizacion_precio=datetime.now(),
                                          usuario_modificacion=usuario_modificacion,
                                          )
            nueva_cotizacion.save()
            if importacion.proveedor:
                nueva_cotizacion.proveedor_asociado = importacion.proveedor
        for n in lista_con_cantidades:
            precio_asociado = n[0].precio
            precio_asociado.nombre_cotizacion = (
                "Importacion" + importacion.codigo_referencial
            )
            if Producto_proyecto.objects.filter(
                producto=proyecto, proyecto=n[0].producto
            ).exists():
                nuevo_producto_proyecto = Producto_proyecto.objects.get(
                    producto=proyecto, proyecto=n[0].producto
                )
                nuevo_producto_proyecto.estado_cotizacion = "Precio"
                nuevo_producto_proyecto.usuario_modificacion = usuario_modificacion
                if importacion.proveedor:
                    nuevo_producto_proyecto.proveedores.add(importacion.proveedor)
                nuevo_producto_proyecto.save()
                if importacion_antigua:
                    for x in importacion_antigua.productos.all():
                        if x.producto == nuevo_producto_proyecto.proyecto:
                            producto_proyecto_cantidades_en_cotizacion = list(
                                Producto_proyecto_cantidades.objects.filter(
                                    proyecto_asociado_cantidades=proyecto,
                                    producto_asociado_cantidades=nuevo_producto_proyecto,
                                )
                            ).pop()
                            producto_proyecto_cantidades_en_cotizacion.precio = (
                                precio_asociado
                            )
                            producto_proyecto_cantidades_en_cotizacion.precio.save()
                            nuevo_producto_proyecto.precio = precio_asociado
                            nuevo_producto_proyecto.save()
                            producto_proyecto_cantidades_en_cotizacion.save()
                else:
                    nuevo_producto_cantidades = Producto_proyecto_cantidades(
                        id=uuid.uuid1(),
                        proyecto_asociado_cantidades=proyecto,
                        producto_asociado_cantidades=nuevo_producto_proyecto,
                        precio=precio_asociado,
                        cantidades=nuevo_producto_proyecto.cantidades,
                    )
                    nuevo_producto_cantidades.save()
                    nueva_cotizacion.productos_asociados.add(n[0].producto)
                    nueva_cotizacion.productos_proyecto_asociados.add(
                        nuevo_producto_cantidades
                    )
                    nueva_cotizacion.save()
            else:
                nuevo_producto_proyecto = Producto_proyecto(
                    id=uuid.uuid1(),
                    producto=proyecto,
                    proyecto=n[0].producto,
                    estado_cotizacion="Precio",
                    cantidades=n[1],
                    usuario_modificacion=usuario_modificacion,
                )
                nuevo_producto_proyecto.save()
                if importacion.proveedor:
                    nuevo_producto_proyecto.proveedores.add(importacion.proveedor)
                nuevo_producto_proyecto.save()
                nuevo_producto_cantidades = Producto_proyecto_cantidades(
                    id=uuid.uuid1(),
                    proyecto_asociado_cantidades=proyecto,
                    producto_asociado_cantidades=nuevo_producto_proyecto,
                    precio=precio_asociado,
                    cantidades=n[1],
                )
                nuevo_producto_cantidades.save()
                nueva_cotizacion.productos_asociados.add(n[0].producto)
                nueva_cotizacion.productos_proyecto_asociados.add(
                    nuevo_producto_cantidades
                )
                nueva_cotizacion.save()
        if not importacion_antigua:
            nueva_orden_compra = Orden_compra(
                id=uuid.uuid1(),
                cotizacion_padre=nueva_cotizacion,
                cotizacion_hija=nueva_cotizacion,
                condicion_entrega="Inmediato",
                condiciones_pago="Importacion",
                forma_pago="Importacion",
                fecha_envio=datetime.now(),
            )
            nueva_orden_compra.save()
        return redirect("/proyectos/proyecto/{}".format(post["importacion"]))

def agregar_calculo(request, id):
    proyecto = Proyecto.objects.get(id=id)
    if request.method == "POST":
        instalacion = InstalacionProyecto.objects.get(nombre=request.POST["instalacion"])
        productos_asociados = instalacion.productos_asociados.all()
        instalacion.proyecto = proyecto
        instalacion.save()
        for i in productos_asociados:
            i.proyecto_asociado_cantidades = proyecto
            nuevo_producto_proyecto = Producto_proyecto(
                    id=uuid.uuid1(),
                    producto=proyecto,
                    proyecto=i.producto,
                    usuario_modificacion=request.user.nombre + " " + request.user.apellido,
                    cantidades = i.cantidades,
                    estado_cotizacion="No",
                )
            nuevo_producto_proyecto.save()
            i.producto_asociado_cantidades = nuevo_producto_proyecto
            i.save()
        return redirect("/proyectos/proyecto/{}".format(proyecto.id))
    else:
        instalaciones_proyecto = InstalacionProyecto.objects.all()
        payload = {
            "Proyecto":proyecto,
                "Instalaciones": instalaciones_proyecto,
            }
        return render(request, "proyectos/agregar_calculo.html", payload)
