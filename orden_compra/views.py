from django.shortcuts import render, redirect
from planificador.models import Orden_compra, Cotizacion, RMC, Producto_proyecto, Producto, Producto_proyecto_cantidades, Producto_proveedor, Precio, Usuario
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date, datetime
from planificador.decorators import allowed_users
from django.contrib.auth.models import User, Permission
import uuid

def excel_oc(id_orden_compra):
    orden_compra = Orden_compra.objects.get(id=id)
    proveedor = orden_compra.cotizacion_hija.proveedor_asociado
    productos = orden_compra.cotizacion_hija.productos_proyecto_asociados.all()
    suma_productos = 0
    for producto in productos:
        if Producto_proveedor.objects.filter(proyecto=producto.producto_asociado_cantidades.proyecto, producto=proveedor).exists():
            nombre_producto =  Producto_proveedor.objects.filter(proyecto=producto.producto_asociado_cantidades.proyecto, producto=proveedor).nombre_proveedor
        else:
            nombre_producto = producto.producto_asociado_cantidades.proyecto.nombre
        cantidad = producto.producto_asociado_cantidades.cantidades
        unidad = producto.producto_asociado_cantidades.proyecto.unidad
        lista_precios = producto.producto_asociado_cantidades.proyecto.lista_precios.all()

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
        nuevo_nombre = cotizacion_padre.nombre+" - " + id_orden
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
            nueva_orden_compra = Orden_compra(id=id_orden, cotizacion_padre=cotizacion_padre, cotizacion_hija=nueva_cotizacion, condicion_entrega=condicion_entrega, condiciones_pago=condicion_pago, forma_pago=forma_pago, destino_factura=destino_factura, observaciones=observaciones)
        else:
            nueva_orden_compra = Orden_compra(id=id_orden, cotizacion_padre=cotizacion_padre, cotizacion_hija=nueva_cotizacion, condicion_entrega=condicion_entrega, condiciones_pago=condicion_pago, forma_pago=forma_pago, destino_factura=destino_factura)
        nueva_orden_compra.save()
        planificadores = User.objects.filter(groups__name='Planificador')
        for i in planificadores:
            usuario_planificador = Usuario.objects.get(correo=i.email)
            if not usuario_planificador.orden_compra:
                usuario_planificador.orden_compra = 0
                usuario_planificador.save()
            usuario_planificador.orden_compra -= 1
            usuario_planificador.save()
        usuario_cotizador = Usuario.objects.get(correo=request.user.email)
        if not usuario_cotizador.orden_compra:
            usuario_cotizador.orden_compra = 0
            usuario_cotizador.save()
        usuario_cotizador.orden_compra -= 1
        usuario_cotizador.save()
        return redirect('/proyectos/mostrar_cotizacion/{}'.format(nueva_cotizacion.id))

def editar_orden(request, id):
    orden_compra = Orden_compra.objects.get(id=id)
    if request.method == "GET":
        productos = orden_compra.cotizacion_hija.productos_proyecto_asociados.all()
        return render(request, "orden_compra/editar_orden.html", {"orden_compra":orden_compra, "productos":productos})
    else:
        condicion_entrega = request.POST["condicion_entrega"]
        condicion_pago = request.POST["condicion_pago"]
        forma_pago = request.POST["forma_pago"]
        empresa = request.POST["empresa"]
        destino_factura = RMC.objects.get(rut=empresa)
        observaciones = request.POST["observaciones"]
        productos = request.POST.getlist("id_producto")
        orden_compra.condicion_entrega = condicion_entrega
        orden_compra.condiciones_pago = condicion_pago
        orden_compra.forma_pago = forma_pago
        orden_compra.destino_factura = destino_factura
        orden_compra.observaciones = observaciones
        orden_compra.save()
        cotizacion_hija = Cotizacion.objects.get(id=orden_compra.cotizacion_hija.id)
        for i in cotizacion_hija.productos_proyecto_asociados.all():
            cantidades = request.POST[i.id]
            producto_asociado =  cotizacion_hija.productos_proyecto_asociados.filter(id=i.id)[0]
            for n in productos:
                if producto_asociado.id == n:
                    producto_asociado.cantidades = cantidades
                    producto_asociado.save()
        return redirect('/proyectos/mostrar_cotizacion/{}'.format(orden_compra.cotizacion_hija.id))

def editar_status(request, id):
    orden_compra = Orden_compra.objects.get(id=id)
    if request.method == "GET":
        return render(request, "orden_compra/editar_status.html", {"orden_compra":orden_compra})
    else:
        status_financiero = request.POST["status_financiero"]
        status_llegada = request.POST["status_llegada"]
        orden_compra.status_financiero = status_financiero
        orden_compra.status_llegada = status_llegada
        orden_compra.save()
        return redirect('/proyectos/mostrar_cotizacion/{}'.format(orden_compra.cotizacion_hija.id))
