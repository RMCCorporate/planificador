from django.shortcuts import render, redirect
from planificador.models import Orden_compra, Cotizacion, RMC, Producto_proyecto, Producto, Correlativo_orden_compra, Producto_proyecto_cantidades
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date, datetime
from planificador.decorators import allowed_users
import uuid


def crear_orden(request, id):
    if request.method == "GET":
        cotizacion_padre = Cotizacion.objects.get(id=id)
        productos_proyecto = []
        for producto in cotizacion_padre.productos_asociados.all():
            producto_proyecto = Producto_proyecto.objects.get(producto=cotizacion_padre.proyecto_asociado, proyecto=producto)
            productos_proyecto.append(producto_proyecto)
        return render(request, "orden_compra/crear_orden.html", {"cotizacion_padre":cotizacion_padre, "productos":productos_proyecto})
    else:
        id_cotizacion = request.POST["id_cotizacion"]
        id_orden = request.POST["id"]
        condicion_entrega = request.POST["condicion_entrega"]
        condicion_pago = request.POST["condicion_pago"]
        forma_pago =request.POST["forma_pago"]
        factura = request.POST["empresa"]
        observaciones = request.POST["observaciones"]
        productos = request.POST.getlist("id_producto")
        cotizacion_padre = Cotizacion.objects.get(id=id_cotizacion)
        if Correlativo_orden_compra.objects.filter(id=cotizacion_padre.id).exists():
            numero_correlativo = str(Correlativo_orden_compra.objects.filter(id=cotizacion_padre.id)[0].numero)
            cambio_correlativo = Correlativo_orden_compra.objects.get(id=cotizacion_padre.id)
            cambio_correlativo.numero += 1
            cambio_correlativo.save()
            nuevo_nombre = cotizacion_padre.nombre+" - " + numero_correlativo
        else:
            nuevo_correlativo = Correlativo_orden_compra(id=cotizacion_padre.id, numero=0)
            nuevo_correlativo.save()
            nuevo_nombre = str(nuevo_correlativo.numero)
        nueva_cotizacion = Cotizacion(id=uuid.uuid1(), nombre=nuevo_nombre, proyecto_asociado=cotizacion_padre.proyecto_asociado, orden_compra=True, proveedor_asociado=cotizacion_padre.proveedor_asociado, usuario_modificacion=cotizacion_padre.usuario_modificacion)
        nueva_cotizacion.save()
        for i in cotizacion_padre.contacto_asociado.all():
            nueva_cotizacion.contacto_asociado.add(i)
            nueva_cotizacion.save()
        if cotizacion_padre.fecha_salida:
            nueva_cotizacion.fecha_salida = cotizacion_padre.fecha_salida
        if cotizacion_padre.fecha_respuesta:
            nueva_cotizacion.fecha_respuesta = cotizacion_padre.fecha_respuesta
        if cotizacion_padre.fecha_actualizacion_precio:
            nueva_cotizacion.fecha_actualizacion_precio = cotizacion_padre.fecha_actualizacion_precio
        nueva_cotizacion.save()
        for i in productos:
            producto_proyecto = Producto_proyecto.objects.get(id=i)
            producto = producto_proyecto.proyecto
            cantidad = request.POST[i]
            nuevo_producto_proyecto_proyecto = Producto_proyecto_cantidades(id=uuid.uuid1(), proyecto_asociado_cantidades=cotizacion_padre.proyecto_asociado, producto_asociado_cantidades=producto_proyecto, cantidades=cantidad)
            nuevo_producto_proyecto_proyecto.save()
            nueva_cotizacion.productos_asociados.add(producto)
            nueva_cotizacion.productos_proyecto_asociados.add(nuevo_producto_proyecto_proyecto)
            nueva_cotizacion.save()
        if RMC.objects.filter(rut = factura).exists():
            destino_factura = RMC.objects.filter(rut = factura)[0]
        else:
            if factura == "76021113-3":
                nuevo_RMC = RMC(rut="76021113-3", nombre="INGENIERÍA Y SERVICIOS RMC LIMITADA", giro="Servicios de Ingeniería", direccion="Pasaje Las Cinerarias 550, Concón - Viña del Mar")
            elif factura == "77241485-4":
                nuevo_RMC = RMC(rut="76021113-3", nombre="RMC INDUSTRIAL SPA", giro="Servicios de Ingeniería", direccion="Pasaje Las Cinerarias 550, Concón - Viña del Mar")
            elif factura == "77241488-9":
                nuevo_RMC = RMC(rut="77241488-9", nombre="RMC EQUIPMENTS SPA", giro="Servicios de Ingeniería", direccion="Pasaje Las Cinerarias 550, Concón - Viña del Mar")
            elif factura == "77289504-6":
                nuevo_RMC = RMC(rut="77289504-6", nombre="RMC CORPORATE SPA", giro="Servicios de Ingeniería", direccion="Pasaje Las Cinerarias 550, Concón - Viña del Mar")
            elif factura == "77077958-8":
                nuevo_RMC = RMC(rut="77077958-8", nombre="RMC LABS SPA", giro="Servicios de Ingeniería", direccion="Pasaje Las Cinerarias 550, Concón - Viña del Mar")
            else:
                nuevo_RMC = RMC(rut="76021113-3", nombre="INGENIERÍA Y SERVICIOS RMC LIMITADA", giro="Servicios de Ingeniería", direccion="Pasaje Las Cinerarias 550, Concón - Viña del Mar")
            nuevo_RMC.save()
            destino_factura = nuevo_RMC
        if observaciones:
            nueva_orden_compra = Orden_compra(id=uuid.uuid1(), cotizacion_padre=cotizacion_padre, cotizacion_hija=nueva_cotizacion, condicion_entrega=condicion_entrega, condiciones_pago=condicion_pago, forma_pago=forma_pago, destino_factura=destino_factura, observaciones=observaciones)
        else:
            nueva_orden_compra = Orden_compra(id=uuid.uuid1(), cotizacion_padre=cotizacion_padre, cotizacion_hija=nueva_cotizacion, condicion_entrega=condicion_entrega, condiciones_pago=condicion_pago, forma_pago=forma_pago, destino_factura=destino_factura)
        nueva_orden_compra.save()
        return redirect('/proyectos/mostrar_cotizacion/{}'.format(nueva_cotizacion.id))
    