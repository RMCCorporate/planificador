from django.shortcuts import render, redirect
from planificador.models import (
    Importaciones,
    DHL,
    Destination_charges,
    Airfreight_charges,
    Origin_charges,
    Producto_proyecto_cantidades,
    Precio,
    Producto,
    Proveedor,
)
from planificador.filters import (
    Filtro_productoFilter,
)
from django.contrib.auth.decorators import login_required
from datetime import datetime
from planificador.filters import Filtro_producto
from planificador.decorators import allowed_users
import openpyxl
import uuid
import json
import requests


class Mindicador:
    def __init__(self, indicador, day, month, year):
        self.indicador = indicador
        self.year = year
        self.month = month
        self.day = day

    def InfoApi(self):
        url = f"https://mindicador.cl/api/{self.indicador}/{self.day}-{self.month}-{self.year}"
        response = requests.get(url)
        data = json.loads(response.text.encode("utf-8"))
        return data


def calculo_flete(flete, kilos):
    valor_flete = 0
    if 45 > kilos and kilos * flete.freight_less_45 > flete.freight_min:
        valor_flete += kilos * flete.freight_less_45
    elif 45 > kilos and not kilos * flete.freight_less_45 > flete.freight_min:
        valor_flete += kilos * flete.freight_less_45
    elif 100 > kilos > 45 and kilos * flete.freight_45_100 > flete.freight_min:
        valor_flete += kilos * flete.freight_45_100
    elif 100 > kilos > 45 and not kilos * flete.freight_45_100 > flete.freight_min:
        valor_flete += flete.freight_min
    elif 300 > kilos > 100 and kilos * flete.freight_100_300 > flete.freight_min:
        valor_flete += kilos * flete.freight_100_300
    elif 300 > kilos > 100 and not kilos * flete.freight_100_300 > flete.freight_min:
        valor_flete += flete.freight_min
    elif 500 > kilos > 300 and kilos * flete.freight_300_500 > flete.freight_min:
        valor_flete += kilos * flete.freight_300_500
    elif 500 > kilos > 300 and not kilos * flete.freight_300_500 > flete.freight_min:
        valor_flete += flete.freight_min
    elif 1000 > kilos > 500 and kilos * flete.freight_500_1000 > flete.freight_min:
        valor_flete += kilos * flete.freight_500_1000
    elif 1000 > kilos > 500 and not kilos * flete.freight_500_1000 > flete.freight_min:
        valor_flete += flete.freight_min
    elif kilos > 1000 and kilos * flete.freight_more_1000 > flete.freight_min:
        valor_flete += kilos * flete.freight_more_1000
    elif kilos > 1000 and not kilos * flete.freight_more_1000 > flete.freight_min:
        valor_flete += flete.freight_min
    if kilos * flete.security_surcharge_kg > flete.security_surcharge_min:
        valor_flete += kilos * flete.security_surcharge_kg
    else:
        valor_flete += flete.security_surcharge_min
    if kilos * flete.cargo_screening_fee_kg > flete.cargo_screening_fee_min:
        valor_flete += kilos * flete.cargo_screening_fee_kg
    else:
        valor_flete += flete.cargo_screening_fee_min
    if kilos * flete.fuel_surcharge_kg > flete.fuel_surcharge_min:
        valor_flete += kilos * flete.fuel_surcharge_kg
    else:
        valor_flete += flete.fuel_surcharge_min
    return valor_flete


def calculo_origen(origen, kilos):
    valor_origen = 0
    if origen.pickup_kg * kilos > origen.pickup_min:
        valor_origen += origen.pickup_kg * kilos
    else:
        valor_origen += origen.pickup_min
    valor_origen += origen.handling + origen.customs_clearence
    if origen.other_fees1_description:
        valor_origen += origen.other_fees1_value_min
    if origen.other_fees2_description:
        if kilos * origen.other_fees2_value_kg > origen.other_fees2_value_min:
            valor_origen += kilos * origen.other_fees2_value_kg
        else:
            valor_origen += origen.other_fees2_value_min
    return valor_origen


def calculo_destino(destino, kilos):
    valor_destino = destino.terminal_handling + destino.desconsolidation
    if destino.doc_fee_max > kilos * destino.doc_fee_kg > destino.doc_fee_min:
        valor_destino += kilos * destino.doc_fee_kg
    elif kilos * destino.doc_fee_kg > destino.doc_fee_max:
        valor_destino += destino.doc_fee_max
    elif destino.doc_fee_min > kilos * destino.doc_fee_kg:
        valor_destino += destino.doc_fee_min
    return valor_destino


@login_required(login_url="/login")
def importaciones(request):
    importaciones = Importaciones.objects.all()
    lenght = len(importaciones)
    payload = {
        "importaciones": importaciones,
        "len": lenght
    }
    return render(request, "importaciones/importaciones.html", payload)


def nueva_importacion_planilla(request):
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb["Air Rates Vertical Format"]
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            region = row_data[1]
            if (
                region != "None"
                and region != "Origin"
                and region != "Region\n(enter AP, AM, EURO, MEA)"
            ):
                country = row_data[2]
                origin = row_data[4]
                if row_data[10] == "Air Economy":
                    origin = origin + "-" + "AE"
                elif row_data[10] == "Air Priority":
                    origin = origin + "-" + "AP"
                if row_data[13] != "On Request":
                    origin_currency = row_data[13]
                    pickup_min = row_data[14]
                    pickup_kg = row_data[15]
                    handling = row_data[16]
                    customs_clearence = row_data[17]
                    if row_data[18] == "None":
                        other_fees1_description = "No hay"
                        other_fees1_value_min = 0
                    else:
                        other_fees1_description = row_data[18]
                        other_fees1_value_min = row_data[19]
                    if row_data[20] == "None":
                        other_fees2_description = "No hay"
                        other_fees2_value_min = 0
                        other_fees2_value_kg = 0
                    else:
                        other_fees2_description = row_data[20]
                        other_fees2_value_min = row_data[21]
                        other_fees2_value_kg = row_data[22]
                    origin_transit_time = row_data[23]
                    origin_charges = Origin_charges(
                        origin_airport=origin,
                        currency=origin_currency,
                        pickup_min=pickup_min,
                        pickup_kg=pickup_kg,
                        handling=handling,
                        customs_clearence=customs_clearence,
                        other_fees1_description=other_fees1_description,
                        other_fees1_value_min=other_fees1_value_min,
                        other_fees2_description=other_fees2_description,
                        other_fees2_value_min=other_fees2_value_min,
                        other_fees2_value_kg=other_fees2_value_kg,
                        origin_transit_time=origin_transit_time,
                    )
                    origin_charges.save()
                    freight_currency = row_data[24]
                    freight_min = row_data[25]
                    freight_less_45 = row_data[26]
                    freight_45_100 = row_data[27]
                    freight_100_300 = row_data[28]
                    freight_300_500 = row_data[29]
                    freight_500_1000 = row_data[30]
                    freight_more_1000 = row_data[31]
                    if row_data[32] == "None" or row_data[32] == "All in":
                        fuel_surcharge_min = 0
                        fuel_surcharge_kg = 0
                    else:
                        fuel_surcharge_min = row_data[32]
                        fuel_surcharge_kg = row_data[33]
                    if row_data[34] == "None" or row_data[34] == "All in":
                        security_surcharge_min = 0
                        security_surcharge_kg = 0
                    else:
                        security_surcharge_min = row_data[34]
                        security_surcharge_kg = row_data[35]
                    if row_data[36] == "None" or row_data[36] == "All in":
                        cargo_screening_fee_min = 0
                        cargo_screening_fee_kg = 0
                    else:
                        cargo_screening_fee_min = row_data[36]
                        cargo_screening_fee_kg = row_data[37]
                    airfreight_charges = Airfreight_charges(
                        origin_airport=origin,
                        currency=freight_currency,
                        freight_min=freight_min,
                        freight_less_45=freight_less_45,
                        freight_45_100=freight_45_100,
                        freight_100_300=freight_100_300,
                        freight_300_500=freight_300_500,
                        freight_500_1000=freight_500_1000,
                        freight_more_1000=freight_more_1000,
                        fuel_surcharge_min=fuel_surcharge_min,
                        fuel_surcharge_kg=fuel_surcharge_kg,
                        security_surcharge_min=security_surcharge_min,
                        security_surcharge_kg=security_surcharge_kg,
                        cargo_screening_fee_min=cargo_screening_fee_min,
                        cargo_screening_fee_kg=cargo_screening_fee_kg,
                    )
                    airfreight_charges.save()
                    airline = row_data[38]
                    direct_flight = row_data[39]
                    departure_days = row_data[40]
                    transit_time = row_data[41]
                    if row_data[42] == "None":
                        destination_currency = "No hay"
                    else:
                        destination_currency = row_data[42]
                    if row_data[43] == "None":
                        terminal_handling = 0
                    else:
                        terminal_handling = row_data[43]
                    if row_data[44] == "None":
                        doc_fee_min = 0
                        doc_fee_max = 0
                        doc_fee_kg = 0
                    else:
                        doc_fee_min = row_data[44]
                        doc_fee_max = row_data[46]
                        doc_fee_kg = row_data[45]
                    if row_data[47] == "None":
                        desconsolidation = 0
                    else:
                        desconsolidation = row_data[47]
                    destination_charges = Destination_charges(
                        origin_airport=origin,
                        currency=destination_currency,
                        terminal_handling=terminal_handling,
                        doc_fee_min=doc_fee_min,
                        doc_fee_max=doc_fee_max,
                        doc_fee_kg=doc_fee_kg,
                        desconsolidation=desconsolidation,
                    )
                    destination_charges.save()
                    dhl = DHL(
                        origin_airport=origin,
                        region=region,
                        country=country,
                        priority=row_data[10],
                        airline=airline,
                        direct_flight=direct_flight,
                        departure_days=departure_days,
                        transit_time=transit_time,
                    )
                    dhl.save()
                    dhl.origin = origin_charges
                    dhl.freight = airfreight_charges
                    dhl.destination = destination_charges
                    dhl.save()
        return redirect("/importaciones")
    else:
        return render(request, "importaciones/nueva_importacion_planilla.html")


@login_required(login_url="/login")
def tarifarios(request):
    tarifarios = DHL.objects.all()
    lenght = len(tarifarios)
    payload = {
        "tarifarios": tarifarios,
        "len": lenght
    }
    return render(request, "importaciones/tarifarios.html", payload)


@login_required(login_url="/login")
def tarifario(request, origin):
    tarifario = DHL.objects.get(origin_airport=origin)
    origen = Origin_charges.objects.get(origin_airport=origin)
    freight = Airfreight_charges.objects.get(origin_airport=origin)
    destino = Destination_charges.objects.get(origin_airport=origin)
    payload = {
        "Tarifario": tarifario,
        "origen": origen,
        "freight": freight,
        "destino": destino,
    }
    return render(request, "importaciones/tarifario.html", payload)


@allowed_users(allowed_roles=["Admin", "Cotizador"])
@login_required(login_url="/login")
def nueva_cotizacion_importacion(request):
    if request.method == "POST":
        post = request.POST
        advalorem = request.POST["advalorem"]
        dhl = DHL.objects.get(origin_airport=post["origen_DHL"])
        valor_flete = calculo_flete(dhl.freight, float(post["kilos"]))
        valor_origen = calculo_origen(dhl.origin, float(post["kilos"]))
        valor_destino = calculo_destino(dhl.destination, float(post["kilos"]))
        objeto_proveedor = Proveedor.objects.get(rut=post["proveedor"])
        advalorem = (1 if advalorem == "SI" else 0)
        nueva_importacion = Importaciones(
            codigo=uuid.uuid1(),
            codigo_referencial=post["codigo"],
            valor_dolar=post["valor_dolar"],
            proveedor=objeto_proveedor,
            origen=dhl.origin_airport,
            DHL_asociado=dhl,
            kilos=float(post["kilos"]),
            valor_flete=valor_flete,
            valor_origen=valor_origen,
            valor_destino=valor_destino,
            moneda_importacion=dhl.origin.currency,
            valor_moneda_importacion=float(post["valor_moneda"]),
            advalorem=advalorem,
            fecha_emision=datetime.now(),
            UF=float(post["UF"]),
        )
        nueva_importacion.save()
        productos = Filtro_producto.objects.all()
        productos_importacion = nueva_importacion.productos.all()
        myFilter = Filtro_productoFilter(request.GET, queryset=productos)
        payload = {
            "Importacion": nueva_importacion,
            "myFilter": myFilter,
            "productos_importacion": productos_importacion,
        }
        return render(request, "importaciones/eleccion_productos.html", payload)
    else:
        lista_dhl = DHL.objects.all()
        proveedores = Proveedor.objects.all()
        dia = str(datetime.today().day)
        mes = str(datetime.today().month)
        año = str(datetime.today().year)
        clase_uf = Mindicador("uf", dia, mes, año)
        uf = float(clase_uf.InfoApi()["serie"][0]["valor"])
        clase_dolar = Mindicador("dolar", dia, mes, año)
        dolar = float(clase_dolar.InfoApi()["serie"][0]["valor"])
        clase_euro = Mindicador("euro", dia, mes, año)
        euro = float(clase_euro.InfoApi()["serie"][0]["valor"])
        payload = {
            "lista_dhl": lista_dhl,
            "proveedores": proveedores,
            "uf": uf,
            "dolar": dolar,
            "euro": euro,
            "dia": dia,
            "mes": mes,
            "año": año,
        }
        return render(request, "importaciones/nueva_cotizacion_importacion.html", payload)


@login_required(login_url="/login")
def importacion(request, importacion):
    importacion = Importaciones.objects.get(codigo=importacion)
    DHL = importacion.DHL_asociado
    productos = importacion.productos.all()
    payload = {
        "Importacion": importacion,
        "DHL": DHL,
        "productos": productos
    }
    return render(request, "importaciones/importacion.html", payload)


@allowed_users(allowed_roles=["Admin", "Cotizador"])
@login_required(login_url="/login")
def anadir_importacion(request):
    if request.method == "POST":
        post = request.POST
        destino = (0 if not post["destino"] else float(post["destino"]))
        advalorem = (1 if post["advalorem"] == "SI" else 0)
        proveedor = post["proveedor"]
        objeto_proveedor = Proveedor.objects.get(rut=proveedor)
        nueva_importacion = Importaciones(
            codigo=uuid.uuid1(),
            codigo_referencial=post["codigo"],
            origen=post["nombre_origen"],
            transporte=post["transporte"],
            proveedor=objeto_proveedor,
            kilos=float(post["kilos"]),
            valor_dolar=float(post["dolar"]),
            valor_flete=float(post["flete"]),
            valor_origen=float(post["origen"]),
            valor_destino=destino,
            moneda_importacion=post["tipo_cambio"],
            valor_moneda_importacion=float(post["valor_cambio"]),
            advalorem=advalorem,
            fecha_emision=post["fecha_emision"],
            fecha_llegada=post["fecha_llegada"],
            UF=float(post["UF"]),
        )
        nueva_importacion.save()
        productos = Filtro_producto.objects.all()
        productos_importacion = nueva_importacion.productos.all()
        myFilter = Filtro_productoFilter(request.GET, queryset=productos)
        payload = {
            "Importacion": nueva_importacion,
            "myFilter": myFilter,
            "productos_importacion": productos_importacion,
        }
        return render(request, "importaciones/eleccion_productos.html", payload)
    else:
        proveedores = Proveedor.objects.all()
        dia = str(datetime.today().day)
        mes = str(datetime.today().month)
        año = str(datetime.today().year)
        clase_uf = Mindicador("uf", dia, mes, año)
        uf = float(clase_uf.InfoApi()["serie"][0]["valor"])
        clase_dolar = Mindicador("dolar", dia, mes, año)
        dolar = float(clase_dolar.InfoApi()["serie"][0]["valor"])
        clase_euro = Mindicador("euro", dia, mes, año)
        euro = float(clase_euro.InfoApi()["serie"][0]["valor"])
        payload = {
            "proveedores": proveedores,
            "uf": uf,
            "dolar": dolar,
            "euro": euro,
            "dia": dia,
            "mes": mes,
            "año": año,
        }
        return render(request, "importaciones/anadir_importacion.html", payload)


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def guardar_datos_filtro(request):
    get = request.GET
    importacion = Importaciones.objects.get(codigo=get["importacion"])
    productos_proyecto_anterior = importacion.productos.all()
    productos_filtro = get.getlist("productos")
    for i in productos_filtro:
        if not productos_proyecto_anterior.filter(producto__nombre=i).exists():
            producto = Producto.objects.get(nombre=i)
            nuevo_producto_importacion = Producto_proyecto_cantidades(
                id=uuid.uuid1(), producto=producto
            )
            nuevo_producto_importacion.save()
            importacion.productos.add(nuevo_producto_importacion)
    productos_proyecto = importacion.productos.all()
    productos = Filtro_producto.objects.all()
    for i in productos_proyecto:
        if productos.filter(nombre_producto=i.producto.nombre):
            s = productos.filter(nombre_producto=i.producto.nombre)[0]
            s.utilizado = importacion.codigo
            s.save()
    myFilter = Filtro_productoFilter(get, queryset=productos)
    payload = {
        "Importacion": importacion,
        "myFilter": myFilter,
        "productos_proyecto": productos_proyecto,
    }
    return render(request, "importaciones/eleccion_productos.html", payload)


@allowed_users(allowed_roles=["Admin", "Planificador"])
@login_required(login_url="/login")
def recibir_datos_planificador(request):
    if request.method == "POST":
        post = request.POST
        usuario = request.user.first_name + " " + request.user.last_name
        importacion = Importaciones.objects.get(codigo=request.GET["importacion"])
        productos = post.getlist("id_producto")
        cantidad = post.getlist("cantidad")
        precio = post.getlist("precio")
        suma_productos = 0
        for n, i in enumerate(precio):
            suma_productos += (
                float(i) * float(cantidad[n]) * importacion.valor_moneda_importacion
            )
        lista_proporcion = []
        for n, i in enumerate(precio):
            lista_proporcion.append(
                float(i)
                * float(cantidad[n])
                * importacion.valor_moneda_importacion
                / suma_productos
            )
        importacion.costo_producto = suma_productos
        importacion.save()
        valor_gasto_despacho = float(importacion.UF)
        valor_honorario = 0
        valor_total = 0
        for counter, i in enumerate(productos):
            if cantidad[counter]:
                valor_total += (
                    float(precio[counter])
                    * importacion.valor_moneda_importacion
                    * float(cantidad[counter])
                )
        CIF = (
            valor_total
            + importacion.valor_flete * importacion.valor_moneda_importacion
            + importacion.valor_origen * importacion.valor_moneda_importacion
        )
        if importacion.advalorem == 0:
            importacion.advalorem = CIF * 0.06
        else:
            importacion.advalorem = 0
        if (CIF * 0.0025) > float(importacion.UF) * 2:
            valor_honorario = (
                valor_total
                + importacion.valor_flete * importacion.valor_moneda_importacion
                + importacion.valor_origen * importacion.valor_moneda_importacion
            ) * 0.0025
        else:
            valor_honorario = 2 * float(importacion.UF)
        importacion.gastos_despacho = valor_gasto_despacho
        importacion.honorarios = valor_honorario
        importacion.save()
        if importacion.DHL_asociado:
            valor_importacion = (
                importacion.valor_flete * importacion.valor_moneda_importacion
                + importacion.valor_origen * importacion.valor_moneda_importacion
                + importacion.valor_destino * importacion.valor_dolar
                + importacion.gastos_despacho
                + importacion.honorarios
            )
        else:
            valor_importacion = (
                importacion.valor_flete * importacion.valor_moneda_importacion
                + importacion.valor_origen * importacion.valor_moneda_importacion
                + importacion.valor_destino
                + importacion.gastos_despacho
                + importacion.honorarios
            )
        valor_importacion_proporcional = []
        for n, i in enumerate(lista_proporcion):
            valor_importacion_proporcional.append(
                i * valor_importacion / float(cantidad[n])
            )
        valor_total = 0
        for counter, i in enumerate(productos):
            nuevo_producto = Producto_proyecto_cantidades.objects.get(id=i)
            if cantidad[counter]:
                nuevo_producto.cantidades = float(cantidad[counter])
            else:
                nuevo_producto.cantidades = 0
            if importacion.proveedor:
                nuevo_precio = Precio(
                    id=uuid.uuid1(),
                    valor=float(precio[counter]),
                    valor_importación=valor_importacion_proporcional[counter],
                    tipo_cambio=importacion.moneda_importacion,
                    valor_cambio=importacion.valor_moneda_importacion,
                    fecha=importacion.fecha_llegada,
                    nombre_proveedor=importacion.proveedor.nombre,
                    nombre_importacion=importacion.codigo,
                    usuario_modificacion=usuario,
                )
                nuevo_precio.save()
            else:
                nuevo_precio = Precio(
                    id=uuid.uuid1(),
                    valor=float(precio[counter]),
                    valor_importación=valor_importacion_proporcional[counter],
                    tipo_cambio=importacion.moneda_importacion,
                    valor_cambio=importacion.valor_moneda_importacion,
                    fecha=importacion.fecha_llegada,
                    nombre_importacion=importacion.codigo,
                    usuario_modificacion=usuario,
                )
                nuevo_precio.save()
            nuevo_producto.precio = nuevo_precio
            nuevo_producto.save()
            producto = nuevo_producto.producto
            producto.lista_precios.add(nuevo_precio)
            producto.save()
        return redirect("/importaciones")
    else:
        importacion = Importaciones.objects.get(codigo=request.GET["importacion"])
        productos_repetidos = request.GET.getlist("productos_checkeados")
        productos = list(dict.fromkeys(productos_repetidos))
        payload = {"Importacion": importacion, "Productos": importacion.productos.all()}
        return render(request, "importaciones/lista_productos.html", payload)
