from django.shortcuts import render, redirect
from planificador.models import Clase, SubClase, Producto, Proveedor, Contacto, Proyecto, Producto_proyecto, Precio, Filtro_producto, Cotizacion, Usuario, Producto_proveedor, Correlativo_cotizacion, Notificacion, Permisos_notificacion
from planificador.filters import ProductoFilter, SubclaseFilter, Filtro_productoFilter, ProyectosFilter
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date, datetime
from planificador.decorators import allowed_users
import uuid

lista_producto_general = []
#Funciones:
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
    texto_html = """<meta http-equiv='Content-Type' content='text/html; charset=UTF-8'/>
<style>@import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:ital,wght@0,400;1,300&display=swap');</style>
<td style="height:5px; max-height:5px; font-size:4px; mso-line-height-rule:exactly; line-height:4px;">--</td>
<table style=" margin:0; padding:0 5px 0 0;">
	<tr>
    <!--Columna Logo-->
		<td style=" margin:0; padding:0; vertical-align:top;">
			<a href='http://www.rmc.cl' title="RMC Engineering Solutions" style="border:none; text-decoration:none;">
        <img moz-do-not-send="true" src="http://rmc.cl/signature_img/rmc_engineering.png" alt="" style="border:none; width:59px; height:59px; display:block;">
      </a>
		</td>
    <!--Columna Info + Representacion-->
		<td style="margin:0; padding:0;">
      <table cellspacing='0' cellpadding='0' border-spacing='0' style="padding:0; margin:0; font-family: 'Roboto Condensed', Helvetica, Arial, sans-serif; font-size:12px; mso-line-height-rule:exactly; line-height:11px; color: rgb(33, 33, 33); border-collapse:collapse; -webkit-text-size-adjust:none;">
				<!--Fila Nombre-->
				<tr style="margin:0;padding:0;">
          <td style="margin:0;padding:2px 0 0 0; font-family: 'Roboto Condensed', Helvetica, Arial, sans-serif; white-space:nowrap;">
            <strong>
              <a href="mailto:{}" style="border:none; text-decoration:none; color: rgb(33, 33, 33);"><span style="color: rgb(33, 33, 33);">{}</span></a>
            </strong>
          </td>
        </tr>
        <tr style="height:5px; max-height:5px; font-size:4px; mso-line-height-rule:exactly; line-height:4px;">
          <td style="height:5px; max-height:5px; font-size:4px; mso-line-height-rule:exactly; line-height:4px;">&nbsp;</td>
        </tr>
				<!--Fila cargo-->
        <tr style="margin:0; padding:0;">
          <td style="margin:0; padding:0; font-family: 'Roboto Condensed', Helvetica, Arial, sans-serif; white-space:nowrap;">
            <span style="color: rgb(33, 33, 33);"><i>{} - RMC Corporate</i></span>
          </td>
        </tr>
        <tr style="height:3px; max-height:3px; font-size:4px; mso-line-height-rule:exactly; line-height:3px;">
          <td style="height:3px; max-height:3px; font-size:4px; mso-line-height-rule:exactly; line-height:3px;">&nbsp;</td>
        </tr>
				<!--Fila Direccion-->
        <tr style="margin:0;padding:0;">
          <td style="margin:0;padding:0;font-family: 'Roboto Condensed', Helvetica, Arial, sans-serif; white-space:nowrap;">
            <span style="color: rgb(33, 33, 33);"><i>Las Cinerarias #550 - Concón</i></span>
          </td>
        </tr>
        <tr style="height:3px; max-height:3px; font-size:4px; mso-line-height-rule:exactly; line-height:3px;">
          <td style="height:3px; max-height:3px; font-size:4px; mso-line-height-rule:exactly; line-height:3px;">&nbsp;</td>
        </tr>
				<!--Fila Telefono-->
        <tr style="margin:0; padding:0;">
          <td style="margin:0; padding:0; font-family: 'Roboto Condensed', Helvetica, Arial, sans-serif; white-space:nowrap;">
            <span style="color: rgb(33, 33, 33);"><i>C. {} - T.{}</i></span>
          </td>
        </tr>
        <tr style="height:3px; max-height:3px; font-size:4px; mso-line-height-rule:exactly; line-height:3px;">
          <td style="height:3px; max-height:3px; font-size:4px; mso-line-height-rule:exactly; line-height:3px;">&nbsp;</td>
        </tr>
				<!--Fila representantes-->
        <tr style="margin:0; padding:0;">
          <td style="margin:0; padding:0; vertical-align:middle;">
              <img moz-do-not-send="true" src="http://rmc.cl/signature_img/empresas_rep.png" alt="" style="border:none; width:280px; display:block;">
      		</td>
        </tr>
      </table>
    </td>
  </tr>
</table>
<td style="height:5px; max-height:5px; font-size:4px; mso-line-height-rule:exactly; line-height:4px;">&nbsp;</td>
""".format(usuario.correo, usuario.nombre + " " + usuario.apellido + " " + usuario.segundo_apellido[0].upper() + ".", usuario.cargo,  usuario.celular, usuario.telefono)
    texto_correo = ""
    texto_lista_productos = ""
    for i in cotizacion.productos_asociados.all():
        #ACA AGREGAR LO DE LOS NOMBRE DE PRODUCTOS
        producto_proyecto = Producto_proyecto.objects.get(producto=cotizacion.proyecto_asociado, proyecto=i)
        nombre = i.nombre
        if Producto_proveedor.objects.filter(proyecto=i, producto=cotizacion.proveedor_asociado).exists():
            nombre = Producto_proveedor.objects.get(proyecto=i, producto=cotizacion.proveedor_asociado).nombre_proveedor
        texto_lista_productos += "\n- {}: {} {}\n".format(nombre, producto_proyecto.cantidades, i.unidad)
    for i in cotizacion.contacto_asociado.all():
        texto_español = "Estimado {}, \nSe solicita cotización de: \n{} \n{}\nSaludos.".format(
            i.nombre,
            texto_lista_productos,
            texto_extra
        )
        texto_ingles = "Dear {}, \nA quote is requested for: \n {} \nRegards.".format(
            i.nombre,
            texto_lista_productos,
            texto_extra
        )
        if cotizacion.proveedor_asociado.idioma == "ESP":
            texto_correo = texto_español
        else:
            texto_correo = texto_ingles
        correo_enviador = usuario.correo
        clave_enviador = clave
        #CAMBIAR A "i.correo"
        correo_prueba = "tacorrea@uc.cl"
        mensaje = MIMEMultipart()
        mensaje['From'] = correo_enviador
        mensaje['To'] = correo_prueba
        mensaje['Subject'] = subject
        mensaje.attach(MIMEText(texto_correo, 'plain'))
        mensaje.attach(MIMEText(texto_html, 'html'))
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(correo_enviador, clave_enviador)
        text = mensaje.as_string()
        session.sendmail(correo_enviador, correo_prueba, text)
        session.quit()
    for i in cotizacion.productos_asociados.all():
        producto_proyecto = Producto_proyecto.objects.get(producto=cotizacion.proyecto_asociado, proyecto=i)
        producto_proyecto.estado_cotizacion = "Enviada"

def crear_notificacion(tipo, correo_usuario, accion, modelo_base_datos, numero_modificado, id_modelo, nombre, id_proyecto):
    hora_actual = datetime.now()
    usuario = Usuario.objects.get(correo=correo_usuario)
    permiso_notificacion = Permisos_notificacion.objects.get(nombre=tipo)
    notificacion = Notificacion(id=uuid.uuid1(), tipo=tipo, accion=accion, modelo_base_datos=modelo_base_datos, numero_modificado=numero_modificado, id_modelo=id_modelo, nombre=nombre, id_proyecto=id_proyecto, fecha=hora_actual)
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
                notificacion.fecha
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
                notificacion.fecha
                )
        #CAMBIAR A SUPPLY
        correo_enviador = 'logistica@rmc.cl'
        clave_enviador = 'RMC.1234'
        #CAMBIAR A i.correo
        correo_prueba = 'tacorreahucke@gmail.com'
        mensaje = MIMEMultipart()
        mensaje['From'] = correo_enviador
        mensaje['To'] = correo_prueba
        mensaje['Subject'] = 'NOTIFICACIÓN {}'.format(notificacion.tipo)
        mensaje.attach(MIMEText(texto_correo, 'plain'))
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(correo_enviador, clave_enviador)
        text = mensaje.as_string()
        session.sendmail(correo_enviador, correo_prueba, text)
        session.quit()
           
# Vista proyectos
@login_required(login_url='/login')
def proyectos(request):
    proyectos = Proyecto.objects.all()
    lenght = len(proyectos)
    myFilter = ProyectosFilter(request.GET, queryset=proyectos)
    return render(request, "proyectos/proyectos.html", {"Proyectos":proyectos, "len":lenght, "myFilter":myFilter})

@login_required(login_url='/login')
def proyecto(request, id):
    usuario = str(request.user.groups.all()[0])
    proyecto = Proyecto.objects.get(id=id)
    productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
    aux_productos_final = []
    cotizaciones = Cotizacion.objects.filter(proyecto_asociado=proyecto)
    precio_final = 0
    lista_productos_precio = []
    lista_cotizaciones = []
    for i in cotizaciones:
        aux_productos = []
        aux = []
        aux.append(i)
        aux3 = []
        for producto in i.productos_asociados.all():
            aux2 = []
            aux2_productos = []
            precio = ""
            producto_proyecto = Producto_proyecto.objects.get(proyecto=producto, producto=proyecto)
            producto_asociado = producto_proyecto.proyecto
            subclase = producto_asociado.subclase_set.all()
            precio = list(producto_asociado.lista_precios.all())
            for n in precio:
                if n.nombre_cotizacion == i.nombre:
                    precio = n
            if precio != []:
                lista_productos_precio.append(producto.nombre)
                aux2_productos.append(producto_asociado)
                aux2_productos.append(subclase)
                aux2_productos.append(producto_proyecto)
                aux2_productos.append(precio)
                aux2_productos.append(i)
                aux_productos.append(aux2_productos)
            aux2.append(producto)
            aux2.append(producto_proyecto)
            demora_respuesta = 0
            aux2.append(demora_respuesta)
            aux3.append(aux2)
        aux_productos_final.append(aux_productos)
        aux.append(aux3)
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
        if i.fecha_actualizacion_precio and i.fecha_respuesta:
            demora_precio = i.fecha_actualizacion_precio - i.fecha_respuesta
        else:
            demora_precio = 0
        aux.append(demora_respuesta)
        aux.append(demora_precio)
        aux.append(estado)
        lista_cotizaciones.append(aux)
    lista_precio = list(dict.fromkeys(lista_productos_precio))
    if len(lista_precio) == len(productos_proyecto):
        proyecto.estado = 'Completo'
        proyecto.save()
    else:
        proyecto.estado = 'Incompleto'
        proyecto.save()
    #PRECIOS
    for i in productos_proyecto:
        precios = i.proyecto.lista_precios.all()
        if len(precios) != 0:
            a = list(precios).pop()
            ultimo_precio = a.valor
        if a.valor_cambio:
            ultimo_precio = a.valor * a.valor_cambio
        if i.cantidades:
            ultimo_precio = ultimo_precio*i.cantidades
        else:
            ultimo_precio = 0
        if a.valor_importación:
            ultimo_precio += a.valor_importación*a.valor_cambio
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
    return render(request, "proyectos/proyecto.html", {"Proyecto":proyecto, "Productos":productos_proyecto, "cotizaciones":lista_cotizaciones, "info_productos":aux_productos_final, "precio":precio_final, "rol": usuario})

@allowed_users(allowed_roles=['Admin', 'Cotizador'])
@login_required(login_url='/login')
def editar_precios(request, id):
    if request.method == "POST":
        proyecto = Proyecto.objects.get(id=id)
        usuario_modificacion = request.user.first_name + " " + request.user.last_name
        productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
        id = request.POST.getlist("id")
        nombre = request.POST.getlist("nombre")
        valor = request.POST.getlist("valor")
        valor_importacion = request.POST.getlist("valor_importacion")
        tipo_cambio = request.POST.getlist("tipo_cambio")
        valor_cambio = request.POST.getlist("valor_cambio")
        cotizacion = []
        #lista_cotizacion = request.POST.getlist("cotizacion")
        for n,i in enumerate(nombre):
            nombre_producto = request.POST[i]
            if nombre_producto != "no_hay":
                cotizacion_nueva = Cotizacion.objects.get(nombre=nombre_producto)
                cotizacion.append(cotizacion_nueva)
                productos_proyecto[n].proveedores.add(cotizacion_nueva.proveedor_asociado)
                productos_proyecto[n].save()
            else:
                cotizacion.append(" ")
        notificacion = False
        for n, producto in enumerate(id):
            #contador = 0
            producto = Producto.objects.get(id=producto)
            producto_proyecto = Producto_proyecto.objects.get(producto=proyecto, proyecto=producto)
            if valor[n] != "None" and valor[n] != "" and cotizacion[n] != " ":
                if valor_importacion[n] != "None" and valor_importacion[n] != "":
                    if valor_cambio[n] == "None" and valor_cambio[n] != "":
                        valor_cambio = 1
                    fecha_actual = datetime.now()
                    if valor_cambio == 1:
                        precio = Precio(id=uuid.uuid1(), valor=valor[n], valor_importación=valor_importacion[n], fecha=fecha_actual, tipo_cambio=tipo_cambio[n], valor_cambio=valor_cambio,  nombre_proveedor=cotizacion[n].proveedor_asociado.nombre, nombre_cotizacion=cotizacion[n].nombre, usuario_modificacion=usuario_modificacion)
                    else:
                        precio = Precio(id=uuid.uuid1(), valor=valor[n], valor_importación=valor_importacion[n], fecha=fecha_actual, tipo_cambio=tipo_cambio[n], valor_cambio=valor_cambio[n],  nombre_proveedor=cotizacion[n].proveedor_asociado.nombre, nombre_cotizacion=cotizacion[n].nombre, usuario_modificacion=usuario_modificacion)
                    precio.save()
                    cotizacion[n].fecha_actualizacion_precio = datetime.now()
                    cotizacion[n].save()
                    usuario = Usuario.objects.get(correo=request.user.email)
                    usuario.precios.add(precio)
                    usuario.save()
                    notificacion = True
                else:
                    fecha_actual = datetime.now()
                    precio = Precio(id=uuid.uuid1(), valor=valor[n], fecha=fecha_actual, nombre_proveedor=cotizacion[n].proveedor_asociado.nombre, nombre_cotizacion=cotizacion[n].nombre, usuario_modificacion=usuario_modificacion)
                    precio.save()
                    cotizacion[n].fecha_actualizacion_precio = datetime.now()
                    cotizacion[n].save()
                    usuario = Usuario.objects.get(correo=request.user.email)
                    usuario.precios.add(precio)
                    usuario.save()
                    notificacion = True
                producto.lista_precios.add(precio)
                producto.save()
                producto_proyecto.estado_cotizacion = "Precio"
                producto_proyecto.save()
        if notificacion:
            crear_notificacion("editar_precio", request.user.email, "editó precio", "Precio y Cotización", len(id), proyecto.id, proyecto.nombre, proyecto.id)
        #Renderizar
        return redirect('/proyectos/proyecto/{}'.format(proyecto.id))
    else:
        proyecto = Proyecto.objects.get(id=id)
        productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
        lista_info_productos = []
        for i in productos_proyecto:
            lista_aux = []
            if i.estado_cotizacion != "No" and i.estado_cotizacion != None and i.estado_cotizacion != "":
                producto = Producto.objects.get(nombre=i.proyecto)
                ultimo_precio = list(producto.lista_precios.all())
                if len(ultimo_precio) != 0:
                    ultimo_precio = ultimo_precio.pop()
                aux_productos = []
                cotizacion = Cotizacion.objects.filter(proyecto_asociado=proyecto)
                for x in cotizacion:
                    for n in x.productos_asociados.all():
                        if n.nombre == i.proyecto.nombre:
                            aux_productos.append(x)
                lista_aux.append(i)
                lista_aux.append(ultimo_precio)
                if aux_productos == []:
                    aux_productos = ["no_hay"]
                lista_aux.append(aux_productos)
                lista_info_productos.append(lista_aux)
        #RENDERIZADO
        return render(request, "proyectos/editar_precio.html", {"info_productos":lista_info_productos})

@allowed_users(allowed_roles=['Admin', 'Planificador'])
@login_required(login_url='/login')
def editar_datos_producto_proyecto(request, id):
    if request.method == "POST":
        proyecto = Proyecto.objects.get(id=id)
        usuario_modificacion = request.user.first_name + " " + request.user.last_name
        cotizaciones = Cotizacion.objects.filter(proyecto_asociado=proyecto)
        nombre = request.POST.getlist("nombre")
        id = request.POST.getlist("id")
        cantidades = request.POST.getlist("cantidades")
        fecha_uso = request.POST.getlist("fecha_uso")
        status = []
        for i in id:
            if request.POST[str(i)] != "no_hay":
                status.append(request.POST[str(i)])
            else:
                status.append(" ")
        for n, i in enumerate(nombre):
            producto = Producto.objects.get(nombre=i)
            producto_proyecto = Producto_proyecto.objects.get(producto=proyecto, proyecto=producto)
            producto_proyecto.cantidades = float(cantidades[n])
            producto_proyecto.status = status[n]
            if fecha_uso[n] != "None" and fecha_uso[n] != "":
                producto_proyecto.fecha_uso = fecha_uso[n]
            producto_proyecto.usuario_modificacion = usuario_modificacion
            producto_proyecto.save()
            usuario = Usuario.objects.get(correo=request.user.email)
            usuario.productos_proyecto.add(producto_proyecto)
            usuario.save()
        crear_notificacion("editar_producto_proyecto", request.user.email, "editó información de producto proyecto", "Producto_proyecto", len(nombre), proyecto.id, proyecto.nombre, proyecto.id)
        eliminar = request.POST.getlist("eliminar")
        if eliminar:
            for i in eliminar:
                producto_eliminar = Producto_proyecto.objects.get(id=i)
                for i in cotizaciones:
                    for n in i.productos_asociados.all():
                        if n.nombre == producto_eliminar.proyecto.nombre:
                            i.productos_asociados.remove(n)
                producto_eliminar.delete()
                usuario = Usuario.objects.get(correo=request.user.email)
                usuario.productos_proyecto.remove(producto_eliminar)
            crear_notificacion("eliminar_producto_proyecto", request.user.email, "eliminó producto proyecto", "Producto_proyecto", len(eliminar), proyecto.id, proyecto.nombre, proyecto.id)
        return redirect('/proyectos/proyecto/{}'.format(proyecto.id))
    else:
        proyecto = Proyecto.objects.get(id=id)
        productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
        lista_info_productos = []
        for i in productos_proyecto:
            lista_aux = []
            producto = Producto.objects.get(nombre=i.proyecto)
            ultimo_precio = list(producto.lista_precios.all())
            if len(ultimo_precio) != 0:
                ultimo_precio = ultimo_precio.pop()
            lista_aux.append(i)
            lista_aux.append(ultimo_precio)
            lista_info_productos.append(lista_aux)
        return render(request, "proyectos/editar_producto_proyecto.html", {"info_productos":lista_info_productos})

@login_required(login_url='/login')
def editar_fechas(request, id):
    proyecto = Proyecto.objects.get(id=id)
    if request.method == "POST":
        proyecto.fecha_inicio = request.POST["fecha_inicio"]
        proyecto.fecha_final = request.POST["fecha_termino"]
        proyecto.save()
        return redirect('/proyectos/proyecto/{}'.format(proyecto.id))
    else:
        return render(request, "proyectos/editar_fechas.html", {"Proyecto":proyecto})

@allowed_users(allowed_roles=['Admin', 'Planificador'])
@login_required(login_url='/login')
def agregar_producto(request, id):
    if request.method == "GET":
        if request.path_info == "/agregar_producto/lista_productos_agregar":
            id = request.GET["id"]
            instancia_proyecto = Proyecto.objects.get(id=id)
            productos = request.GET.getlist("productos_checkeados")
            lista_productos = []
            if productos:
                for i in productos:
                    aux = []
                    instancia_producto = Producto.objects.get(nombre=i)
                    sub_clase = instancia_producto.subclase_set.all()[0]
                    aux.append(instancia_producto)
                    aux.append(sub_clase)
                    if Producto_proyecto.objects.filter(producto=instancia_proyecto, proyecto=instancia_producto).exists():
                        aux.append(Producto_proyecto.objects.get(producto=instancia_proyecto, proyecto=instancia_producto))
                    lista_productos.append(aux)
                if Proveedor.objects.filter(subclases_asociadas=sub_clase).exists():
                    proveedores = Proveedor.objects.filter(subclases_asociadas=sub_clase)
                return render(request, "proyectos/crear_producto_proyecto.html", {"Proyecto":instancia_proyecto, "Producto":lista_productos, "Proveedores":proveedores})
            else:
                error = "No se ingresó ningún producto."
                return render(request, "error_general.html", {"error":error})
        else:
            if id == "guardar_datos_filtro_agregar_proyecto":
                id = request.GET["id"]
            proyecto = Proyecto.objects.get(id=id)
            nuevo_productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
            productos = Filtro_producto.objects.all()
            myFilter = Filtro_productoFilter(request.GET, queryset=productos)
            lista_productos = []
            return render(request, "proyectos/agregar_producto.html", {"id":id, "Proyecto":proyecto, "myFilter":myFilter, "productos_proyecto":nuevo_productos_proyecto})
    elif request.method == "POST":
        productos_filtro = request.POST.getlist("producto")
        usuario_modificacion = request.user.first_name + " " + request.user.last_name
        id_ql = request.POST["id"]
        proyecto = Proyecto.objects.get(id=id_ql)
        productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
        for i in productos_filtro:
            booleano_repeticion = False
            for n in productos_proyecto:
                if n.proyecto.nombre == i:
                    booleano_repeticion = True
            if not booleano_repeticion and i:
                producto = Producto.objects.get(nombre=i)
                nuevo_producto_proyecto = Producto_proyecto(id=uuid.uuid1(), producto=proyecto, proyecto=producto, usuario_modificacion=usuario_modificacion, estado_cotizacion="No")
                nuevo_producto_proyecto.save()
        productos = Filtro_producto.objects.all()
        myFilter = Filtro_productoFilter(request.GET, queryset=productos)
        producto = myFilter.qs
        nuevo_productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
        return render(request, 'proyectos/agregar_producto.html', {"id":id_ql, "Proyecto":proyecto, "myFilter":myFilter, "productos_proyecto":nuevo_productos_proyecto})

@login_required(login_url='/login')
def crear_nuevo_producto(request):
    usuario_modificacion = request.user.first_name + " " + request.user.last_name
    proyecto = Proyecto.objects.get(id=request.POST["id_proyecto"])
    productos = request.POST.getlist("id_producto")
    fechas_uso = request.POST.getlist("fecha_uso")
    cantidades = request.POST.getlist("cantidades")
    for n, i in enumerate(productos):
        status = request.POST[i]
        producto = Producto.objects.get(id=i)
        if cantidades[n] == "":
            cantidades[n] = 0
        if fechas_uso[n] != "":
            if not Producto_proyecto.objects.filter(producto=proyecto, proyecto=producto).exists():
                nuevo_producto_proyecto = Producto_proyecto(id=uuid.uuid1(), producto=proyecto, proyecto=producto, status=status, fecha_uso=fechas_uso[n], cantidades=cantidades[n], usuario_modificacion=usuario_modificacion, estado_cotizacion="No")
                nuevo_producto_proyecto.save()
                usuario = Usuario.objects.get(correo=request.user.email)
                usuario.productos_proyecto.add(nuevo_producto_proyecto)
                usuario.save()
            else:
                producto_proyecto = Producto_proyecto.objects.get(producto=proyecto, proyecto=producto)
                producto_proyecto.status = status
                producto_proyecto.fecha_uso = fechas_uso[n]
                producto_proyecto.cantidades = cantidades[n]
                producto_proyecto.usuario_modificacion = usuario_modificacion
                producto_proyecto.save()
        else:
            if not Producto_proyecto.objects.filter(producto=proyecto, proyecto=producto).exists():
                nuevo_producto_proyecto = Producto_proyecto(id=uuid.uuid1(), producto=proyecto, proyecto=producto, status=status, cantidades=cantidades[n], usuario_modificacion=usuario_modificacion, estado_cotizacion="No")
                nuevo_producto_proyecto.save()
                usuario = Usuario.objects.get(correo=request.user.email)
                usuario.productos_proyecto.add(nuevo_producto_proyecto)
                usuario.save()
            else:
                producto_proyecto = Producto_proyecto.objects.get(producto=proyecto, proyecto=producto)
                producto_proyecto.status = status
                producto_proyecto.cantidades = cantidades[n]
                producto_proyecto.usuario_modificacion = usuario_modificacion
                producto_proyecto.save()
    crear_notificacion("agregar_producto_proyecto", request.user.email, "creó producto(s) en proyecto", "Producto_Proyecto", len(productos), proyecto.id, proyecto.nombre, proyecto.id)
    return redirect('/proyectos/proyecto/{}'.format(proyecto.id))
    
# Vista planificador I
@login_required(login_url='/login')
def planificador(request):
    usuario = str(request.user)
    if usuario == "tacorrea@uc.cl" or usuario == "pcorrea" or usuario == "rcasascordero" or usuario == "vvergara":
        return render(request, "proyectos/planificador.html")
    else:
        return redirect('/')

@allowed_users(allowed_roles=['Admin', 'Planificador'])
@login_required(login_url='/login')
def mostrar_filtro(request):
    centro_costos = request.GET["centro_costos"]
    nombre = request.GET["nombre"]
    tipo_cambio = request.GET["tipo_cambio"]
    valor_cambio = request.GET["valor_cambio"]
    if not valor_cambio:
        valor_cambio = 0
    if not tipo_cambio:
        tipo_cambio = "CLP"
    fecha_inicio = request.GET["fecha_inicio"]
    fecha_termino = request.GET["fecha_termino"]
    creador = request.user.first_name + " " + request.user.last_name
    fecha_actual = datetime.now()
    if fecha_inicio and fecha_termino:
        nuevo_proyecto = Proyecto(id=centro_costos, nombre=nombre, precio_final=0, fecha_creacion = fecha_actual, fecha_inicio=fecha_inicio, fecha_final=fecha_termino, tipo_cambio=tipo_cambio, valor_cambio=valor_cambio, creador=creador)
        nuevo_proyecto.save()
    elif not fecha_termino and (fecha_inicio and fecha_inicio != "None"):
        nuevo_proyecto = Proyecto(id=centro_costos, nombre=nombre, precio_final=0, fecha_creacion = fecha_actual, fecha_inicio=fecha_inicio, tipo_cambio=tipo_cambio, valor_cambio=valor_cambio, creador=creador)
        nuevo_proyecto.save()
    elif (fecha_termino and fecha_termino != "None") and not fecha_inicio:
        nuevo_proyecto = Proyecto(id=centro_costos, nombre=nombre, precio_final=0, fecha_creacion = fecha_actual, fecha_final=fecha_termino, tipo_cambio=tipo_cambio, valor_cambio=valor_cambio, creador=creador)
        nuevo_proyecto.save()
    else:
        nuevo_proyecto = Proyecto(id=centro_costos, nombre=nombre, precio_final=0, fecha_creacion = fecha_actual, tipo_cambio=tipo_cambio, valor_cambio=valor_cambio, creador=creador)
        nuevo_proyecto.save()
    crear_notificacion("crear_proyecto", request.user.email, "creó un proyecto", "Proyecto", 1, centro_costos, nombre, centro_costos)
    productos = Filtro_producto.objects.all()
    myFilter = Filtro_productoFilter(request.GET, queryset=productos)
    productos_proyecto = nuevo_proyecto.productos.all()
    return render(request, 'proyectos/eleccion_productos.html', {"Proyecto":nuevo_proyecto, "myFilter":myFilter, "productos_proyecto":productos_proyecto})

@allowed_users(allowed_roles=['Admin', 'Planificador'])
@login_required(login_url='/login')
def guardar_datos_filtro(request):
    usuario_modificacion = request.user.first_name + " " + request.user.last_name
    proyecto = Proyecto.objects.get(id=request.GET["centro_costos"])
    productos_proyecto_anterior = proyecto.productos.all()
    productos_filtro = request.GET.getlist("productos")
    booleano_repeticion = False
    for i in productos_filtro:
        for n in productos_proyecto_anterior:
            if n.nombre == i:
                booleano_repeticion = True
    for i in productos_filtro:
        if not booleano_repeticion: 
            producto = Producto.objects.get(nombre=i)
            nuevo_producto_proyecto=Producto_proyecto(id=uuid.uuid1(), producto=proyecto, proyecto=producto, usuario_modificacion=usuario_modificacion, estado_cotizacion="No")
            nuevo_producto_proyecto.save()
            proyecto.save()
            usuario = Usuario.objects.get(correo=request.user.email)
            usuario.proyectos.add(proyecto)
            usuario.save()
    productos_proyecto = proyecto.productos.all()
    productos = Filtro_producto.objects.all()
    myFilter = Filtro_productoFilter(request.GET, queryset=productos)
    producto = myFilter.qs
    return render(request, 'proyectos/eleccion_productos.html', {"Proyecto":proyecto, "myFilter":myFilter, "productos_proyecto":productos_proyecto})

#Recibir vista planificador I
@allowed_users(allowed_roles=['Admin', 'Planificador'])
@login_required(login_url='/login')
def recibir_datos_planificador(request):
    proyecto = Proyecto.objects.get(id=request.GET["centro_costos"])
    productos_repetidos = request.GET.getlist("productos_checkeados")
    productos = list(dict.fromkeys(productos_repetidos))
    lista_subclases_productos = []
    for producto in productos:
        lista_aux_producto = []
        lista_aux_proveedores = []
        instancia_producto = Producto.objects.get(nombre=producto)
        lista_aux_producto.append(instancia_producto)
        subclases_producto = instancia_producto.subclase_set.all()
        subclases_proveedores = Proveedor.objects.filter(subclases_asociadas=subclases_producto[0])
        for i in subclases_proveedores:
            lista_aux_proveedores.append(i)
        lista_aux_producto.append(lista_aux_proveedores)
        subclases_proveedores = []
        lista_subclases_productos.append(lista_aux_producto)
    return render(request, "proyectos/lista_productos.html", {"Proyecto":proyecto, "Productos":lista_subclases_productos})

@allowed_users(allowed_roles=['Admin', 'Planificador'])
@login_required(login_url='/login')
def recibir_cantidades_planificador(request):
    proyecto = Proyecto.objects.get(id=request.GET["centro_costos"])
    cantidad = request.GET.getlist("cantidad")
    productos = request.GET.getlist("id_producto")
    boton = request.GET["boton"]
    for counter, i in enumerate(productos):
        nuevo_producto = Producto.objects.get(nombre=i)
        producto_proyecto = Producto_proyecto.objects.get(producto=proyecto, proyecto=nuevo_producto)
        if cantidad[counter]:
            producto_proyecto.cantidades = float(cantidad[counter])
        else:
            producto_proyecto.cantidades = 0
        producto_proyecto.save()
        usuario = Usuario.objects.get(correo=request.user.email)
        usuario.productos_proyecto.add(producto_proyecto)
        usuario.save()
    if boton == "Guardar y continuar":
        productos = Filtro_producto.objects.all()
        myFilter = Filtro_productoFilter(request.GET, queryset=productos)
        productos_proyecto = proyecto.productos.all()
        return render(request, 'proyectos/eleccion_productos.html', {"Proyecto":proyecto, "myFilter":myFilter, "productos_proyecto":productos_proyecto})
    else:
        return redirect('/proyectos')

@allowed_users(allowed_roles=['Admin', 'Cotizador'])
@login_required(login_url='/login')
def agregar_cotizacion(request, id):
    if request.method == "POST":
        proyecto_asociado = Proyecto.objects.get(id=id)
        usuario_modificacion = request.user.first_name + " " + request.user.last_name
        nombre = request.POST["nombre"]
        info_productos = request.POST.getlist("contacto")
        diccionario_proveedores = {}
        for i in info_productos:
            producto,proveedor,contacto = i.split('**')
            if proveedor not in diccionario_proveedores.keys():
                diccionario_proveedores[proveedor] = [[contacto],[producto]]
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
        if len(str(correlativo.numero)) == 1:
            nombre_con_correlativo =  nombre + " - " + "000" + str(correlativo.numero)
        elif len(str(correlativo.numero)) == 2:
            nombre_con_correlativo =  nombre + " - " + "00" + str(correlativo.numero)
        elif len(str(correlativo.numero)) == 3:
            nombre_con_correlativo =  nombre + " - " + "0" + str(correlativo.numero)
        elif len(str(correlativo.numero)) == 4:
            nombre_con_correlativo =  nombre + " - " + str(correlativo.numero)
        for nombre_proveedor in diccionario_proveedores:
            proveedor = Proveedor.objects.get(nombre=nombre_proveedor)
            nueva_cotizacion = Cotizacion(id=uuid.uuid1(), nombre=nombre_con_correlativo, proyecto_asociado=proyecto_asociado, proveedor_asociado=proveedor, fecha_salida = datetime.now(), usuario_modificacion=usuario_modificacion)
            nueva_cotizacion.save()
            usuario = Usuario.objects.get(correo=str(request.user.email))
            usuario.cotizaciones.add(nueva_cotizacion)
            usuario.save()
            for id in diccionario_proveedores[nombre_proveedor][1]:
                nuevo_producto = Producto.objects.get(id=id)
                nuevo_producto_proyecto = Producto_proyecto.objects.get(producto=proyecto_asociado, proyecto=nuevo_producto)
                nueva_cotizacion.productos_asociados.add(nuevo_producto)
                nueva_cotizacion.save()
                nuevo_producto_proyecto.estado_cotizacion = "Creada"
                nuevo_producto_proyecto.save()
            contactos_sin_repetir = list(dict.fromkeys(diccionario_proveedores[nombre_proveedor][0]))
            for contactos in contactos_sin_repetir:
                contacto_agregar = Contacto.objects.get(nombre=contactos)
                nueva_cotizacion.contacto_asociado.add(contacto_agregar)
                nueva_cotizacion.save()
        crear_notificacion("crear_cotizacion", request.user.email, "creó cotizaciones", "Cotización", 1, nueva_cotizacion.id, nueva_cotizacion.nombre, proyecto_asociado.id)
        return redirect('/proyectos/proyecto/{}'.format(proyecto_asociado.id))
    else:
        proyecto = Proyecto.objects.get(id=id)
        productos = proyecto.productos.all()
        lista_productos = []
        for i in productos:
            lista_producto_proyecto = []
            lista_proveedores = []
            producto_proyecto = Producto_proyecto.objects.filter(producto=proyecto, proyecto=i)
            lista_producto_proyecto.append(producto_proyecto[0])
            proveedores = Proveedor.objects.filter(subclases_asociadas=producto_proyecto[0].proyecto.subclase_set.all()[0])
            for n in proveedores:
                for contacto in n.contactos_asociados.all():
                    aux = []          
                    aux.append(n)
                    aux.append(contacto)
                    lista_proveedores.append(aux)
            lista_producto_proyecto.append(lista_proveedores)
            lista_productos.append(lista_producto_proyecto)
        return render(request, "proyectos/crear_cotizacion.html", {"Proyecto":proyecto, "Proveedores":lista_productos})

@login_required(login_url='/login')
def mostrar_cotizacion(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    productos = []
    for i in cotizacion.productos_asociados.all():
        producto_proyecto = Producto_proyecto.objects.get(producto=cotizacion.proyecto_asociado, proyecto=i)
        productos.append(producto_proyecto)
    contactos = cotizacion.contacto_asociado.all()
    return render(request, "proyectos/cotizacion.html", {"Cotizacion":cotizacion, "Productos":productos, "contactos":contactos})

@allowed_users(allowed_roles=['Admin', 'Cotizador'])
@login_required(login_url='/login')
def editar_cotizacion(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    if request.method == "POST":
        usuario_modificacion = request.user.first_name + " " + request.user.last_name
        cotizacion.nombre = request.POST["nombre"]
        cotizacion.usuario_modificacion = usuario_modificacion
        cotizacion.fecha_respuesta = request.POST["fecha_respuesta"]
        cotizacion.save()
        usuario = Usuario.objects.get(correo=request.user.email)
        usuario.cotizaciones.add(cotizacion)
        usuario.save()
        crear_notificacion("editar_fecha_respuesta_cotización", request.user.email, "editó cotización", "Cotización", 1, cotizacion.id, cotizacion.nombre, cotizacion.proyecto_asociado.id)
        return redirect('/proyectos/mostrar_cotizacion/{}'.format(cotizacion.id))
    else:
        return render(request, "proyectos/editar_cotizacion.html", {"Cotizacion":cotizacion})

@allowed_users(allowed_roles=['Admin', 'Cotizador'])
@login_required(login_url='/login')
def eliminar_cotizacion(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    proyecto = cotizacion.proyecto_asociado.id
    crear_notificacion("eliminar_cotización", request.user.email, "eliminó cotización", "Cotización", 1, cotizacion.id, cotizacion.nombre, cotizacion.proyecto_asociado.id)
    cotizacion.delete()
    return redirect('/proyectos/proyecto/{}'.format(proyecto))

@login_required(login_url='/login')
def enviar_correo(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    proyecto = cotizacion.proyecto_asociado.id
    if request.method == "POST":
        subject = request.POST["subject"]
        texto_extra = request.POST["texto"]
        clave = request.POST["clave"]
        usuario = Usuario.objects.get(correo=request.user.email)
        crear_correo(usuario, cotizacion, texto_extra, clave, subject)
        cotizacion.fecha_salida = datetime.now()
        cotizacion.save()
        crear_notificacion("enviar_correo", request.user.email, "envió correo con cotización", "Cotización", 1, cotizacion.id, cotizacion.nombre, cotizacion.proyecto_asociado.id)
        return redirect('/proyectos/proyecto/{}'.format(proyecto))
    else:
        contacto = cotizacion.contacto_asociado.all()
        return render(request, "proyectos/enviar_correo.html", {"Cotizacion":cotizacion, "contactos":contacto})

