from django.shortcuts import render, redirect
from planificador.models import Clase, SubClase, Producto, Proveedor, Contacto, Proyecto, Producto_proyecto, Precio, Filtro_producto, Cotizacion, Usuario, Producto_proveedor, Correlativo_cotizacion, Notificacion, Permisos_notificacion, Orden_compra, RMC, Presupuesto_subclases, Producto_proyecto_cantidades, Importaciones
from planificador.filters import ProductoFilter, SubclaseFilter, Filtro_productoFilter, ProyectosFilter
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date, datetime
from planificador.decorators import allowed_users
import uuid
from django.contrib.auth.models import User, Permission
from operator import itemgetter
from RMC_Corporate.settings import BASE_DIR, MEDIA_ROOT, MEDIA_URL, EXCEL_ROOT

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
        #CAMBIAR A LOGISTICA
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
    cotizaciones = Cotizacion.objects.filter(proyecto_asociado=proyecto)
    precio_final = 0
    lista_productos_precio = []
    tabla_productos = []
    for i in productos_proyecto:
        aux_tabla_productos = []
        if len(i.proyecto.lista_precios.all()) != 0:
            precio = list(i.proyecto.lista_precios.all()).pop()
        else:
            precio = "No"
        aux_tabla_productos.append(i)
        aux_tabla_productos.append(precio)
        tabla_productos.append(aux_tabla_productos)
    tabla_cotizaciones = []
    tabla_productos_cotizados = []
    for i in cotizaciones:
        aux_tabla_cotizaciones = []
        aux_tabla_cotizaciones_producto_proyecto = []
        aux_demoras = []
        aux_tabla_cotizaciones.append(i)
        for producto in i.productos_asociados.all():
            aux_tabla_productos_cotizados = []
            aux_tabla_cotizaciones_producto_proyecto.append(Producto_proyecto.objects.get(proyecto=producto, producto=proyecto))
            if producto.lista_precios:
                precios = producto.lista_precios.all()
                if precios.filter(nombre_cotizacion=i.nombre, nombre_proveedor=i.proveedor_asociado.nombre).exists():
                    precio = list(precios.filter(nombre_cotizacion=i.nombre, nombre_proveedor=i.proveedor_asociado.nombre)).pop()
                    aux_tabla_productos_cotizados.append(producto)
                    aux_tabla_productos_cotizados.append(precio)
                    tabla_productos_cotizados.append(aux_tabla_productos_cotizados)
                else:
                    precio = ""
        aux_tabla_cotizaciones.append(aux_tabla_cotizaciones_producto_proyecto)
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
        aux_demoras.append(demora_respuesta)
        aux_demoras.append(demora_precio)
        aux_demoras.append(estado)
        aux_tabla_cotizaciones.append(aux_demoras)
        tabla_cotizaciones.append(aux_tabla_cotizaciones)
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
    utilidad_subclase = 0
    for i in proyecto.presupuesto_subclases.all():
        if i.utilidad:
            utilidad_subclase += i.valor*(1+(i.utilidad/100))
    return render(request, "proyectos/proyecto.html", {"Proyecto":proyecto, "Productos":tabla_productos, "cotizaciones":tabla_cotizaciones, "info_productos":tabla_productos_cotizados, "precio":precio_final, "rol": usuario, "utilidad_subclase":utilidad_subclase})

@allowed_users(allowed_roles=['Admin', 'Cotizador'])
@login_required(login_url='/login')
def editar_precios(request, id):
    if request.method == "POST":
        cotizacion = Cotizacion.objects.get(id=id)
        usuario_modificacion = request.user.first_name + " " + request.user.last_name
        id_productos = request.POST.getlist("id_producto")
        valor = request.POST.getlist("valor")
        valor_importacion = request.POST.getlist("valor_importacion")
        tipo_cambio = request.POST.getlist("tipo_cambio")
        valor_cambio = request.POST.getlist("valor_cambio")
        fecha = request.POST.getlist("fecha")
        fecha_actual = date.today()
        for n, producto in enumerate(id_productos):
            producto = Producto.objects.get(id=producto)
            producto_proyecto = Producto_proyecto.objects.get(producto=cotizacion.proyecto_asociado, proyecto=producto)
            if not valor_importacion[n]:
                nuevo_valor_importacion = 0
            else:
                nuevo_valor_importacion = valor_importacion[n]
            if not tipo_cambio[n]:
                nuevo_tipo_cambio = "CLP"
            else:
                nuevo_tipo_cambio = tipo_cambio[n]
            if not valor_cambio[n]:
                nuevo_valor_cambio = 1
            else:
                nuevo_valor_cambio = valor_cambio[n]
            precio = Precio(id=uuid.uuid1(), valor=valor[n], valor_importación=nuevo_valor_importacion, fecha=fecha_actual, tipo_cambio=nuevo_tipo_cambio, valor_cambio=nuevo_valor_cambio,  nombre_proveedor=cotizacion.proveedor_asociado.nombre, nombre_cotizacion=cotizacion.nombre, usuario_modificacion=usuario_modificacion)
            precio.save()
            cotizacion.fecha_actualizacion_precio = datetime.now()
            cotizacion.save()
            usuario = Usuario.objects.get(correo=request.user.email)
            usuario.precios.add(precio)
            usuario.save()
            producto_proyecto.estado_cotizacion = "Precio"
            producto_proyecto.save()
            producto.lista_precios.add(precio)
            producto.save()
            producto_proyecto.estado_cotizacion = "Precio"
            producto_proyecto.save()
        for i in fecha:
            cotizacion.fecha_respuesta = i
            cotizacion.save()
        crear_notificacion("editar_precio", request.user.email, "editó precio", "Precio y Cotización", len(id_productos), cotizacion.proyecto_asociado.id, cotizacion.proyecto_asociado.nombre, cotizacion.proyecto_asociado.id)
        return redirect('/proyectos/proyecto/{}'.format(cotizacion.proyecto_asociado.id))
    else:
        cotizacion = Cotizacion.objects.get(id=id)
        lista_productos = []
        productos = cotizacion.productos_asociados.all()
        for i in productos:
            auxiliar_lista_productos = []
            auxiliar_lista_productos.append(i)
            precios = i.lista_precios.all()
            if precios.filter(nombre_cotizacion=cotizacion.nombre).exists():
                auxiliar_lista_productos.append(precios.filter(nombre_cotizacion=cotizacion.nombre))
            else:
                auxiliar_lista_productos.append([])
            lista_productos.append(auxiliar_lista_productos)
        return render(request, "proyectos/editar_precio.html", {"info_productos":lista_productos, "Cotizacion":cotizacion})

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
        print(myFilter)
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
        subclase_producto = producto.subclase_set.all()[0]
        if not proyecto.presupuesto_subclases.filter(subclase=subclase_producto).exists():
            nuevo_presupuesto_subclase = Presupuesto_subclases(id=uuid.uuid1(), valor=0, subclase=subclase_producto)
            nuevo_presupuesto_subclase.save()
            proyecto.presupuesto_subclases.add(nuevo_presupuesto_subclase)
            proyecto.save()
    crear_notificacion("agregar_producto_proyecto", request.user.email, "creó producto(s) en proyecto", "Producto_Proyecto", len(productos), proyecto.id, proyecto.nombre, proyecto.id)
    return redirect('/proyectos/proyecto/{}'.format(proyecto.id))
    
# Vista planificador I
@login_required(login_url='/login')
def planificador(request):
    print("PASO POR PLANIFICADOR")
    usuario = str(request.user)
    print(usuario)
    if usuario == "tacorrea@uc.cl" or usuario == "pcorrea" or usuario == "rcasascordero" or usuario == "vvergara" or usuario=="tacorrea":
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
    edicion = request.GET["edicion"]
    if edicion == "No" and Proyecto.objects.filter(id=centro_costos).exists():
        return render(request, "proyectos/planificador.html", {"error":"ERROR"})
    else:
        if not valor_cambio:
            valor_cambio = 0
        if not tipo_cambio:
            tipo_cambio = "CLP"
        fecha_inicio = request.GET["fecha_inicio"]
        fecha_termino = request.GET["fecha_termino"]
        creador = request.user.first_name + " " + request.user.last_name
        fecha_actual = datetime.now()
        if fecha_inicio and fecha_termino:
            nuevo_proyecto = Proyecto(id=centro_costos, nombre=nombre, precio_final=0, fecha_creacion = fecha_actual, fecha_inicio=fecha_inicio, fecha_final=fecha_termino, tipo_cambio=tipo_cambio, valor_cambio=valor_cambio, creador=creador, consolidacion=False)
            nuevo_proyecto.save()
        elif not fecha_termino and (fecha_inicio and fecha_inicio != "None"):
            nuevo_proyecto = Proyecto(id=centro_costos, nombre=nombre, precio_final=0, fecha_creacion = fecha_actual, fecha_inicio=fecha_inicio, tipo_cambio=tipo_cambio, valor_cambio=valor_cambio, creador=creador, consolidacion=False)
            nuevo_proyecto.save()
        elif (fecha_termino and fecha_termino != "None") and not fecha_inicio:
            nuevo_proyecto = Proyecto(id=centro_costos, nombre=nombre, precio_final=0, fecha_creacion = fecha_actual, fecha_final=fecha_termino, tipo_cambio=tipo_cambio, valor_cambio=valor_cambio, creador=creador, consolidacion=False)
            nuevo_proyecto.save()
        else:
            nuevo_proyecto = Proyecto(id=centro_costos, nombre=nombre, precio_final=0, fecha_creacion = fecha_actual, tipo_cambio=tipo_cambio, valor_cambio=valor_cambio, creador=creador, consolidacion=False)
            nuevo_proyecto.save()
        crear_notificacion("crear_proyecto", request.user.email, "creó un proyecto", "Proyecto", 1, centro_costos, nombre, centro_costos)
        productos = Filtro_producto.objects.all()
        productos_proyecto = nuevo_proyecto.productos.all()
        myFilter = Filtro_productoFilter(request.GET, queryset=productos)     
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
            if producto.proveedor_interno:
                proveedor_int = Proveedor.objects.get(nombre=producto.proveedor_interno)
                nuevo_producto_proyecto.proveedores.add(proveedor_int)
                nuevo_producto_proyecto.save()
            proyecto.save()
            usuario = Usuario.objects.get(correo=request.user.email)
            usuario.proyectos.add(proyecto)
            usuario.save()
    productos_proyecto = proyecto.productos.all()
    productos = Filtro_producto.objects.all()
    for i in productos_proyecto:
        if productos.filter(nombre_producto=i):
            s = productos.filter(nombre_producto=i)[0]
            s.utilizado = proyecto.id
            s.save()
    myFilter = Filtro_productoFilter(request.GET, queryset=productos)
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
        producto_clase = Producto.objects.get(nombre=producto)
        lista_aux_producto.append(producto_clase)
        if Producto_proyecto.objects.filter(producto=proyecto, proyecto=producto_clase):
            lista_aux_producto.append(Producto_proyecto.objects.filter(producto=proyecto, proyecto=producto_clase)[0])
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
    if boton == "GUARDAR Y CONTINUAR":
        productos = Filtro_producto.objects.all()
        myFilter = Filtro_productoFilter(request.GET, queryset=productos)
        productos_proyecto = proyecto.productos.all()
        return render(request, 'proyectos/eleccion_productos.html', {"Proyecto":proyecto, "myFilter":myFilter, "productos_proyecto":productos_proyecto})
    else:
        lista_subclases = []
        for i in proyecto.productos.all():
            subclase = i.subclase_set.all()[0].nombre
            lista_subclases.append(subclase)
            lista_subclases_final = list(dict.fromkeys(lista_subclases))
        lista_con_utilidad = []
        for i in lista_subclases_final:
            aux = []
            aux.append(i)
            instancia_subclase = SubClase.objects.get(nombre=i)
            if instancia_subclase.utilidad:
                aux.append(instancia_subclase.utilidad)
            else:
                aux.append(0)
            lista_con_utilidad.append(aux)
        return render(request, 'proyectos/eleccion_presupuesto.html', {"Proyecto":proyecto, "subclases":lista_con_utilidad})

@allowed_users(allowed_roles=['Admin', 'Planificador'])
@login_required(login_url='/login')
def eleccion_presupuesto(request, id):
    proyecto = Proyecto.objects.get(id=id)
    subclases = request.POST.getlist("subclases")
    nombre_subclases = request.POST.getlist("subclases_nombres")
    presupuesto_total = request.POST["presupuesto_total"]
    utilidad = request.POST.getlist("utilidad")
    proyecto.presupuesto_total = presupuesto_total
    proyecto.save()
    for n, i in enumerate(subclases):
        modelo_subclase = SubClase.objects.get(nombre=nombre_subclases[n])
        nuevo_presupuesto_subclase = Presupuesto_subclases(id=uuid.uuid1(), valor=i, subclase=modelo_subclase, utilidad=utilidad[n])
        nuevo_presupuesto_subclase.save()
        proyecto.presupuesto_subclases.add(nuevo_presupuesto_subclase)
        proyecto.save()
    return redirect('/proyectos/proyecto/{}'.format(proyecto.id))
    
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
                    no_existe = False
                    for x in n.productos_no.all():
                        if producto_proyecto[0].proyecto.id == x.id:
                            no_existe = True
                    if not no_existe:
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
    if cotizacion.orden_compra:
        orden_compra = Orden_compra.objects.get(cotizacion_hija=cotizacion)
        productos_orden_compra = cotizacion.productos_proyecto_asociados.all()
        for producto in orden_compra.cotizacion_hija.productos_proyecto_asociados.all():
            lista_precio = producto.producto_asociado_cantidades.proyecto.lista_precios.all()
            if lista_precio.filter(nombre_cotizacion=orden_compra.cotizacion_hija.nombre).exists():
                filtro = lista_precio.filter(nombre_cotizacion=orden_compra.cotizacion_hija.nombre)
    else:
        orden_compra = False
        productos_orden_compra = False
    return render(request, "proyectos/cotizacion.html", {"Cotizacion":cotizacion, "Productos":productos, "contactos":contactos, "orden_compra":orden_compra, "productos_orden_compra":productos_orden_compra, "EXCEL_ROOT":EXCEL_ROOT})

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
def editar_disponibilidad(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    if request.method == "POST":
        usuario_modificacion = request.user.first_name + " " + request.user.last_name
        productos = request.POST.getlist("producto")
        proveedor = cotizacion.proveedor_asociado
        for i in productos:
            producto = Producto.objects.get(id=i)
            proveedor.productos_no.add(producto)
            proveedor.save()
        return redirect('/proyectos/mostrar_cotizacion/{}'.format(cotizacion.id))
    else:
        productos_asociados = cotizacion.productos_asociados.all()
        return render(request, "proyectos/editar_disponibilidad.html", {"Cotizacion":cotizacion, "info_productos":productos_asociados})


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

@allowed_users(allowed_roles=['Admin', 'Planificador'])
@login_required(login_url='/login')
def informar_orden_compra(request, id):
    proyecto = Proyecto.objects.get(id=id)
    if request.method == "POST":
        enviar = request.POST["enviar"]
        cotizador = User.objects.filter(email=enviar)
        empresa = request.POST["empresa"]
        observaciones = request.POST["observaciones"]
        productos = request.POST.getlist("nombre")
        productos_cantidades = []
        cantidad_orden_compra = []
        for i in productos:
            aux = []
            nuevo = i.split("*")
            aux.append(nuevo[0])
            aux.append(nuevo[1])
            cantidad_orden_compra.append(nuevo[1])
            aux.append(request.POST[nuevo[2]])
            productos_cantidades.append(aux)
        numero_orden_compra = len(list(dict.fromkeys(cantidad_orden_compra)))
        usuario_cotizador = Usuario.objects.get(correo=enviar)
        if not usuario_cotizador.orden_compra:
            usuario_cotizador.orden_compra = 0
            usuario_cotizador.save()
        usuario_cotizador.orden_compra += numero_orden_compra
        usuario_cotizador.save()
        planificadores = User.objects.filter(groups__name='Planificador')
        for i in planificadores:
            usuario_planificador = Usuario.objects.get(correo=i.email)
            if not usuario_planificador.orden_compra:
                usuario_planificador.orden_compra = 0
                usuario_planificador.save()
            usuario_planificador.orden_compra += numero_orden_compra
            usuario_planificador.save()
        texto_correo = ""
        texto_lista_productos = ""
        texto_entrada = "{} {},\nSe adjunta información para realización de órdenes de compra: \n(Nº Cotización, nombre producto, cantidad) \n\n".format(
            cotizador[0].first_name,
            cotizador[0].last_name
        )
        lista_ordenada = sorted(productos_cantidades, key=itemgetter(1))
        for producto in lista_ordenada:
            texto_productos = "{} - {} - {} \n".format(
                producto[1],
                producto[0],
                producto[2]
            )
            texto_lista_productos += texto_productos
        texto_correo += texto_entrada
        texto_correo += texto_lista_productos
        texto_correo += "\nObservaciones: {}\n".format(observaciones)
        texto_correo += "Facturar a: {} \n".format(empresa)
        #CAMBIAR A LOGISTICA
        correo_enviador = "tcorrea@rmc.cl"
        clave_enviador = "Tom12345"
        #CAMBIAR A "i.correo"
        correo_prueba = "tacorrea@uc.cl"
        mensaje = MIMEMultipart()
        mensaje['From'] = correo_enviador
        mensaje['To'] = correo_prueba
        mensaje['Subject'] = "Crear orden de compra"
        mensaje.attach(MIMEText(texto_correo, 'plain'))
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(correo_enviador, clave_enviador)
        text = mensaje.as_string()
        session.sendmail(correo_enviador, correo_prueba, text)
        session.quit()
        return redirect('/proyectos/proyecto/{}'.format(id))
    else:
        cotizaciones = Cotizacion.objects.filter(proyecto_asociado=proyecto)
        tabla_productos_cotizados = []
        for i in cotizaciones:
            for producto in i.productos_asociados.all():
                aux_tabla_productos_cotizados = []
                if producto.lista_precios:
                    precios = producto.lista_precios.all()
                    if precios.filter(nombre_cotizacion=i.nombre, nombre_proveedor=i.proveedor_asociado.nombre).exists():
                        precio = list(precios.filter(nombre_cotizacion=i.nombre, nombre_proveedor=i.proveedor_asociado.nombre)).pop()
                        aux_tabla_productos_cotizados.append(Producto_proyecto.objects.get(proyecto=producto, producto=proyecto))
                        aux_tabla_productos_cotizados.append(precio)
                        tabla_productos_cotizados.append(aux_tabla_productos_cotizados)
                    else:
                        precio = ""
        cotizadores = User.objects.filter(groups__name='Cotizador')
        return render(request, 'proyectos/informar_orden_compra.html', {"productos":tabla_productos_cotizados, "cotizadores":cotizadores})

@allowed_users(allowed_roles=['Admin', 'Planificador'])
@login_required(login_url='/login')
def editar_presupuesto(request, id):
    proyecto = Proyecto.objects.get(id=id)
    if request.method == "POST":
        presupuesto_total = request.POST["presupuesto_total"]
        proyecto.presupuesto_total = float(presupuesto_total)
        proyecto.save()
        presupuestos_subclases = request.POST.getlist("subclases")
        utilidades = request.POST.getlist("utilidad")
        nombre_presupuestos_subclases = request.POST.getlist("subclases_nombres")
        for n, i in enumerate(presupuestos_subclases):
            for x in proyecto.presupuesto_subclases.all():
                if x.subclase.nombre == nombre_presupuestos_subclases[n]:
                    subclase_encontrada = SubClase.objects.get(nombre=x.subclase.nombre)
                    subclase_final = proyecto.presupuesto_subclases.filter(subclase=subclase_encontrada)[0]
                    subclase_final.valor = float(i)
                    subclase_final.utilidad = float(utilidades[n])
                    subclase_final.save()
        return redirect('/proyectos/proyecto/{}'.format(id))
    else:
        presupuesto_subclases = proyecto.presupuesto_subclases.all()
        return render(request, 'proyectos/editar_presupuesto.html', {"Proyecto":proyecto, "presupuesto_subclases":presupuesto_subclases})

@allowed_users(allowed_roles=['Admin', 'Planificador'])
@login_required(login_url='/login')
def consolidar_proyecto(request, id):
    proyecto = Proyecto.objects.get(id=id)
    proyecto.consolidacion = True
    proyecto.save()
    return redirect('/proyectos/proyecto/{}'.format(id))
   
@allowed_users(allowed_roles=['Admin', 'Planificador'])
@login_required(login_url='/login')
def agregar_orden_interna(request, id):
    proyecto = Proyecto.objects.get(id=id)
    if request.method == "POST":
        usuario_modificacion = request.user.first_name + " " + request.user.last_name
        nombre = request.POST["nombre"]
        condicion_pago = request.POST["condicion_pago"]
        empresa = request.POST["empresa"]
        proveedor = Proveedor.objects.get(rut=empresa)
        observaciones = request.POST["observaciones"]
        productos_escogidos = request.POST.getlist("id_producto")
        lista_proveedor = {}
        for x in productos_escogidos:
            producto = Producto_proyecto.objects.get(id=x)
            auxiliar_proveedor = []
            info_precio_cantidad = request.POST.getlist(x)
            cantidad = info_precio_cantidad[1]
            proveedor = info_precio_cantidad[0]
            precio = info_precio_cantidad[2]
            if proveedor not in lista_proveedor.keys():
                lista_proveedor[proveedor] = [[producto, cantidad, precio]]
            else:
                lista_proveedor[proveedor].append([producto, cantidad, precio])
        for i in lista_proveedor.keys():
            proveedor_asociado = Proveedor.objects.get(nombre=i)
            nueva_cotizacion = Cotizacion(id=uuid.uuid1(), nombre=nombre, proyecto_asociado=proyecto, orden_compra=True, proveedor_asociado=proveedor_asociado, fecha_salida=datetime.now(), fecha_respuesta=datetime.now(), fecha_actualizacion_precio=datetime.now(), usuario_modificacion=usuario_modificacion)
            nueva_cotizacion.save()
            for n in lista_proveedor[i]:
                precio_asociado = Precio(id=uuid.uuid1(), valor=n[2], fecha=datetime.now(), nombre_proveedor=i, nombre_cotizacion=nueva_cotizacion.nombre, usuario_modificacion=usuario_modificacion)
                precio_asociado.save()
                nuevo_producto_cantidades = Producto_proyecto_cantidades(id=uuid.uuid1(), proyecto_asociado_cantidades=proyecto, producto_asociado_cantidades=n[0], precio=precio_asociado, cantidades=n[1])
                nuevo_producto_cantidades.save()
                nueva_cotizacion.productos_asociados.add(n[0].proyecto)
                nueva_cotizacion.productos_proyecto_asociados.add(nuevo_producto_cantidades)
                nueva_cotizacion.save()
            nombre_rmc = RMC.objects.get(rut=empresa)
            nueva_orden_compra = Orden_compra(id=uuid.uuid1(), cotizacion_padre=nueva_cotizacion, cotizacion_hija=nueva_cotizacion, condicion_entrega="Inmediato", condiciones_pago=condicion_pago, forma_pago="Interno", destino_factura=nombre_rmc, observaciones=observaciones)
            nueva_orden_compra.save()
        return redirect('/proyectos/proyecto/{}'.format(id))
    else:
        lista_productos = []
        nombre_RMCs = ["INGENIERÍA Y SERVICIOS RMC LIMITADA", "RMC INDUSTRIAL SPA", "RMC EQUIPMENTS SPA", "RMC CORPORATE SPA", "RMC LABS SPA"]
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
        return render(request, 'proyectos/agregar_orden_interna.html', {"Proyecto":proyecto, "productos":lista_productos})

@allowed_users(allowed_roles=['Admin', 'Planificador'])
@login_required(login_url='/login')
def nueva_importacion(request, id):
    if request.method == "GET":
        if request.path_info == "/nueva_importacion/recibir_importacion":
            id_proyecto = request.GET["centro_costos"]
            proyecto = Proyecto.objects.get(id=id_proyecto)
            codigo_importacion = request.GET["eleccion"]
            importacion = Importaciones.objects.get(codigo=codigo_importacion)
            productos = importacion.productos.all()
            return render(request, 'proyectos/elegir_cantidades_importacion.html', {"Importacion":importacion, "Productos":productos, "Proyecto":proyecto})
        else:
            proyecto = Proyecto.objects.get(id=id)
            importaciones = Importaciones.objects.all()
            lista_importaciones = []
            for i in importaciones:
                lista_importaciones.append(i)
            return render(request, 'proyectos/nueva_importacion.html', {"importaciones":lista_importaciones, "Proyecto":proyecto})
    else:
        usuario_modificacion = request.user.first_name + " " + request.user.last_name
        id_proyecto = request.POST["centro_costos"]
        id_importacion = request.POST["importacion"]
        proyecto = Proyecto.objects.get(id=id_proyecto)
        importacion = Importaciones.objects.get(codigo=id_importacion)
        productos_totales = request.POST.getlist("eleccion")
        productos_escogidos = request.POST.getlist("id_producto")
        cantidades = request.POST.getlist("cantidad")
        lista_con_cantidades = []
        for n, i in enumerate(productos_totales):
            for x in productos_escogidos:
                if i == x:
                    aux = []
                    producto = Producto_proyecto_cantidades.objects.get(id=x)
                    aux.append(producto)
                    aux.append(cantidades[n])
                    lista_con_cantidades.append(aux)
        proveedor_asociado = importacion.proveedor
        nueva_cotizacion = Cotizacion(id=uuid.uuid1(), nombre="Importacion"+importacion.codigo, proyecto_asociado=proyecto, orden_compra=True, proveedor_asociado=proveedor_asociado, fecha_salida=datetime.now(), fecha_respuesta=datetime.now(), fecha_actualizacion_precio=datetime.now(), usuario_modificacion=usuario_modificacion)
        nueva_cotizacion.save()
        for n in lista_con_cantidades:
            precio_asociado = n[0].precio
            if Producto_proyecto.objects.filter(producto=proyecto, proyecto=n[0].producto).exists():
                #YA CREADO: VER QUE SE HACE AQUÍ. LA LÓGICA DIRÍA QUE SE RESTEN LAS CANTIDADES DE LOS PRODUCTOS_PROYECTOS YA EXISTENTES Y SI LLEGAN A 0, SE AÑADAN TODO NUEVO. SINO NOSE QUE WEA.
                nuevo_producto_proyecto = Producto_proyecto.objects.get(producto=proyecto, proyecto=n[0].producto)
                nuevo_producto_proyecto.cantidades += float(n[1])
                nuevo_producto_proyecto.usuario_modificacion = usuario_modificacion
                nuevo_producto_proyecto.proveedores.add(proveedor_asociado)
                nuevo_producto_proyecto.save()
                nuevo_producto_cantidades = Producto_proyecto_cantidades(id=uuid.uuid1(), proyecto_asociado_cantidades=proyecto, producto_asociado_cantidades=nuevo_producto_proyecto, precio=precio_asociado, cantidades=n[1])
                nuevo_producto_cantidades.save()
                nueva_cotizacion.productos_asociados.add(n[0].producto)
                nueva_cotizacion.productos_proyecto_asociados.add(nuevo_producto_cantidades)
                nueva_cotizacion.save()
            else:
                nuevo_producto_proyecto = Producto_proyecto(id=uuid.uuid1(), producto=proyecto, proyecto=n[0].producto, estado_cotizacion="Precio", cantidades=n[1], usuario_modificacion=usuario_modificacion)
                nuevo_producto_proyecto.save()
                nuevo_producto_proyecto.proveedores.add(proveedor_asociado)
                nuevo_producto_proyecto.save()
                nuevo_producto_cantidades = Producto_proyecto_cantidades(id=uuid.uuid1(), proyecto_asociado_cantidades=proyecto, producto_asociado_cantidades=nuevo_producto_proyecto, precio=precio_asociado, cantidades=n[1])
                nuevo_producto_cantidades.save()
                nueva_cotizacion.productos_asociados.add(n[0].producto)
                nueva_cotizacion.productos_proyecto_asociados.add(nuevo_producto_cantidades)
                nueva_cotizacion.save()
        nueva_orden_compra = Orden_compra(id=uuid.uuid1(), cotizacion_padre=nueva_cotizacion, cotizacion_hija=nueva_cotizacion, condicion_entrega="Inmediato", condiciones_pago="Importacion", forma_pago="Importacion", fecha_envio=datetime.now())
        nueva_orden_compra.save()
        return redirect('/proyectos/proyecto/{}'.format(id_proyecto))
