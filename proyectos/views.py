from django.shortcuts import render
from planificador.models import Clase, SubClase, Producto, Proveedor, Contacto, Proyecto, Producto_proyecto, Precio, Filtro_producto, Cotizacion
from planificador.filters import ProductoFilter, SubclaseFilter, Filtro_productoFilter
from django.http import HttpResponse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date, datetime
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

def crear_correo(lista_contacto):
    correo = lista_contacto[1]
    empresa = lista_contacto[2]
    idioma = lista_contacto[3]
    texto_lista_productos = ""
    for producto in lista_contacto[4]:
        texto_lista_productos += "\n- {}: {} {}\n".format(producto[0], producto[1], [producto[2]])
    texto_correo = ""
    texto_español = "Estimado {}, \nSe solicita cotización de: \n {} \nSaludos.".format(
        lista_contacto[0],
        texto_lista_productos
    )
    texto_ingles = "Dear {}, \nA quote is requested for: \n {} \nRegards.".format(
        lista_contacto[0],
        texto_lista_productos
    )
    if idioma == "ESP":
        texto_correo = texto_español
    else:
        texto_correo = texto_ingles
    correo_enviador = 'tcorrea@rmc.cl'
    clave_enviador = 'Tom12345'
    #CAMBIAR DESPUÉS A "CORREO":
    correo_prueba = 'tacorrea@uc.cl'
    mensaje = MIMEMultipart()
    mensaje['From'] = correo_enviador
    mensaje['To'] = correo_prueba
    mensaje['Subject'] = 'Correo de prueba planificador'
    mensaje.attach(MIMEText(texto_correo, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(correo_enviador, clave_enviador)
    text = mensaje.as_string()
    session.sendmail(correo_enviador, correo_prueba, text)
    session.quit()

# Vista proyectos
def proyectos(request):
    proyectos = Proyecto.objects.all()
    return render(request, "proyectos/proyectos.html", {"Proyectos":proyectos})

def proyecto(request, id):
    proyecto = Proyecto.objects.get(id=id)
    productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
    productos = []
    for n, producto in enumerate(productos_proyecto):
        aux = []
        booleano_precio = False
        auxiliar_proveedores = []
        producto_asociado = Producto.objects.get(id=producto.proyecto.id)
        sub_clase = producto_asociado.subclase_set.all()
        aux.append(productos_proyecto[n])
        precio = list(producto_asociado.lista_precios.all())
        if len(precio) != 0:
            precio = precio.pop()
            for i in producto.proveedores.all():
                auxiliar_proveedores.append(i)  
                if i.nombre == precio.nombre_proveedor:
                    booleano_precio = True
        aux.append(producto_asociado)
        aux.append(sub_clase)
        aux.append(auxiliar_proveedores)
        aux.append(precio)
        productos.append(aux)
    cotizaciones = Cotizacion.objects.filter(proyecto_asociado=proyecto)
    lista_cotizaciones = []
    for i in cotizaciones:
        aux = []
        aux.append(i)
        aux3 = []
        for producto in i.productos_asociados.all():
            aux2 = []
            producto_proyecto = Producto_proyecto.objects.get(proyecto=producto, producto=proyecto)
            aux2.append(producto)
            aux2.append(producto_proyecto)
            aux3.append(aux2)
        aux.append(aux3)
        lista_cotizaciones.append(aux)
    return render(request, "proyectos/proyecto.html", {"Proyecto":proyecto, "Productos":productos_proyecto, "info_productos":productos, "cotizaciones":lista_cotizaciones})

def editar_precios(request, id):
    if request.method == "POST":
        proyecto = Proyecto.objects.get(id=id)
        productos_proyecto = Producto_proyecto.objects.filter(producto=proyecto)
        id = request.POST.getlist("id")
        nombre = request.POST.getlist("nombre")
        valor = request.POST.getlist("valor")
        valor_importacion = request.POST.getlist("valor_importacion")
        tipo_cambio = request.POST.getlist("tipo_cambio")
        valor_cambio = request.POST.getlist("valor_cambio")
        proveedor = []
        for n,i in enumerate(nombre):
            if request.POST[str(i)] != "no_hay":
                proveedor.append(request.POST[i])
                nuevo_proveedor = Proveedor.objects.get(nombre=request.POST[i])
                productos_proyecto[n].proveedores.add(nuevo_proveedor)
                productos_proyecto[n].save()
            else:
                proveedor.append(" ")
     
        for n, producto in enumerate(id):
            producto = Producto.objects.get(id=producto)
            if valor[n] != "None" and valor[n] != "":
                if valor_importacion[n] != "None" and valor_importacion[n] != "":
                    if valor_cambio[n] == "None" and valor_cambio[n] != "":
                        valor_cambio = 1
                    fecha_actual = datetime.now()
                    precio = Precio(id=uuid.uuid1(), valor=valor[n], valor_importación=valor_importacion[n], fecha=fecha_actual, tipo_cambio=tipo_cambio[n], valor_cambio=valor_cambio[n],  nombre_proveedor=proveedor[n])
                    precio.save()
                else:
                    fecha_actual = datetime.now()
                    precio = Precio(id=uuid.uuid1(), valor=valor[n], fecha=fecha_actual, nombre_proveedor=proveedor[n])
                    precio.save()
                producto.lista_precios.add(precio)
                producto.save()
            
        #Renderizar
        proyectos = Proyecto.objects.all()
        return render(request, "proyectos/proyectos.html", {"Proyectos":proyectos})
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
            sub_clase = producto.subclase_set.all()[0]
            proveedores = Proveedor.objects.filter(subclases_asociadas=sub_clase)
            lista_aux.append(i)
            lista_aux.append(ultimo_precio)
            lista_aux.append(proveedores)
            lista_info_productos.append(lista_aux)
       
        #RENDERIZADO
        return render(request, "proyectos/editar_precio.html", {"info_productos":lista_info_productos})

def editar_datos_producto_proyecto(request, id):
    if request.method == "POST":
        proyecto = Proyecto.objects.get(id=id)
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
        proveedor = []
        for i in nombre:
            if request.POST[str(i)] != "no_hay":
                proveedor.append(request.POST[i])
            else:
                proveedor.append(" ")
        for n, i in enumerate(nombre):
            producto = Producto.objects.get(nombre=i)
            producto_proyecto = Producto_proyecto.objects.get(producto=proyecto, proyecto=producto)
            producto_proyecto.cantidades = float(cantidades[n])
            producto_proyecto.status = status[n]
            producto_proyecto.fecha_uso = fecha_uso[n]
            booleano_proveedor = True
            for i in producto_proyecto.proveedores.all():
                if i.nombre == proveedor[n]:
                    booleano_proveedor = False
            if booleano_proveedor:
                proveedor_producto = Proveedor.objects.get(nombre=proveedor[n])
                producto_proyecto.proveedores.add(proveedor_producto)
            producto_proyecto.save()
        proyectos = Proyecto.objects.all()
        return render(request, "proyectos/proyectos.html", {"Proyectos":proyectos})
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
            sub_clase = producto.subclase_set.all()[0]
            proveedores = Proveedor.objects.filter(subclases_asociadas=sub_clase)
            lista_aux.append(i)
            lista_aux.append(ultimo_precio)
            lista_aux.append(proveedores)
            lista_info_productos.append(lista_aux)
        return render(request, "proyectos/editar_producto_proyecto.html", {"info_productos":lista_info_productos})

def agregar_producto(request, id):
    if request.method =="POST":
        proyectos = Proyecto.objects.all()
        producto = request.POST["producto"]
        id = request.POST["id"]
        instancia_producto = Producto.objects.get(nombre=producto)
        instancia_proyecto = Proyecto.objects.get(id=id)
        sub_clase = instancia_producto.subclase_set.all()[0]
        proveedores = Proveedor.objects.filter(subclases_asociadas=sub_clase)
        return render(request, "proyectos/crear_producto_proyecto.html", {"Proyecto":instancia_proyecto, "Producto":instancia_producto, "Proveedores":proveedores})
    else:
        proyectos = Proyecto.objects.all()
        clases = Clase.objects.all()
        subclases = []
        nombres = []
        for clase in clases:
            subclases_aux = []
            nombres.append(clase.nombre)
            for subclase in clase.subclases.all():
                subclases_aux.append(subclase)
            subclases.append(subclases_aux)
        lista_clases = []
        for n, i in enumerate(clases):
            lista_aux = []
            lista_aux.append(i)
            lista_aux.append(clases_lista_productos(subclases[n]))
            lista_clases.append(lista_aux)
        productos = Filtro_producto.objects.all()
        myFilter = Filtro_productoFilter(request.GET, queryset=productos)
        producto = myFilter.qs
        #RECIBIR SUBCLASE
        lista_productos = []
        return render(request, "proyectos/agregar_producto.html", {"id":id, "Proyectos":proyectos, "Clases":lista_clases, "myFilter":myFilter, "producto":lista_productos})

def crear_nuevo_producto(request):
    proyecto = Proyecto.objects.get(id=request.POST["id_proyecto"])
    producto = Producto.objects.get(id=request.POST["id_producto"])
    valor = request.POST["valor"]
    valor_importacion = request.POST["valor_importacion"]
    tipo_cambio = request.POST["tipo_cambio"]
    valor_cambio = request.POST["valor_cambio"]
    proveedor = request.POST["proveedor"]
    status = request.POST["status"]
    fecha_uso = request.POST["fecha_uso"]
    cantidades = request.POST["cantidades"]
    fecha_actual = datetime.now()
    if valor == "":
        valor = 0
    if valor_importacion == "":
        valor_importacion = 0
    if tipo_cambio == "":
        tipo_cambio = "CLP"
    if valor_cambio == "":
        valor_cambio = 1
    if status == "no_hay":
        status = "Futuro"
    if cantidades == "":
        cantidades = 0
    nuevo_precio = Precio(id=uuid.uuid1(), valor=valor, valor_importación=valor_importacion, tipo_cambio=tipo_cambio, valor_cambio=valor_cambio, fecha=fecha_actual, nombre_proveedor=proveedor)
    nuevo_precio.save()
    producto.lista_precios.add(nuevo_precio)
    if fecha_uso != "":
        nuevo_producto_proyecto = Producto_proyecto(id=uuid.uuid1(), producto=proyecto, proyecto=producto, status=status, fecha_uso=fecha_uso, cantidades=cantidades)
        nuevo_producto_proyecto.save()
    else:
        nuevo_producto_proyecto = Producto_proyecto(id=uuid.uuid1(), producto=proyecto, proyecto=producto, status=status, cantidades=cantidades)
        nuevo_producto_proyecto.save()
    if proveedor != "no_hay":
        instancia_proveedor = Proveedor.objects.get(nombre=proveedor)
        nuevo_producto_proyecto.proveedores.add(instancia_proveedor)
    proyectos = Proyecto.objects.all()
    return render(request, "proyectos/proyectos.html", {"Proyectos":proyectos})
    
# Vista planificador I
def planificador(request):
    clases = Clase.objects.all()
    subclases = []
    nombres = []
    for clase in clases:
        subclases_aux = []
        nombres.append(clase.nombre)
        for subclase in clase.subclases.all():
            subclases_aux.append(subclase)
        subclases.append(subclases_aux)
    clase1 = clases_lista_productos(subclases[0])
    clase2 = clases_lista_productos(subclases[1])
    clase3 = clases_lista_productos(subclases[2])
    return render(request, "proyectos/planificador.html", {"Nombre1":nombres[0], "Subclases1":clase1, "Nombre2":nombres[1], "Subclases2":clase2, "Nombre3":nombres[2], "Subclases3":clase3})

def mostrar_filtro(request):
    centro_costos = request.GET["centro_costos"]
    nombre = request.GET["nombre"]
    tipo_cambio = request.GET["tipo_cambio"]
    valor_cambio = request.GET["valor_cambio"]
    fecha_inicio = request.GET["fecha_inicio"]
    fecha_termino = request.GET["fecha_termino"]
    precio_final = 0
    #CAMBIAR CREADOR CUANDO SE CREEN USUARIOS
    creador = "Tomás"
    fecha_actual = datetime.now()
    if fecha_inicio and fecha_termino:
        nuevo_proyecto = Proyecto(id=centro_costos, nombre=nombre, precio_final=precio_final, fecha_creacion = fecha_actual, fecha_inicio=fecha_inicio, fecha_final=fecha_termino, tipo_cambio=tipo_cambio, valor_cambio=valor_cambio, creador=creador)
        nuevo_proyecto.save()
    elif not fecha_termino and (fecha_inicio and fecha_inicio != "None"):
        nuevo_proyecto = Proyecto(id=centro_costos, nombre=nombre, precio_final=precio_final, fecha_creacion = fecha_actual, fecha_inicio=fecha_inicio, tipo_cambio=tipo_cambio, valor_cambio=valor_cambio, creador=creador)
        nuevo_proyecto.save()
    elif (fecha_termino and fecha_termino != "None") and not fecha_inicio:
        nuevo_proyecto = Proyecto(id=centro_costos, nombre=nombre, precio_final=precio_final, fecha_creacion = fecha_actual, fecha_final=fecha_termino, tipo_cambio=tipo_cambio, valor_cambio=valor_cambio, creador=creador)
        nuevo_proyecto.save()
    else:
        nuevo_proyecto = Proyecto(id=centro_costos, nombre=nombre, precio_final=precio_final, fecha_creacion = fecha_actual, tipo_cambio=tipo_cambio, valor_cambio=valor_cambio, creador=creador)
        nuevo_proyecto.save()
    #PRODUCTOS:
    productos = Filtro_producto.objects.all()
    myFilter = Filtro_productoFilter(request.GET, queryset=productos)
    producto = myFilter.qs
    lista_producto = list(producto)
    productos_proyecto = nuevo_proyecto.productos.all()
    return render(request, 'proyectos/eleccion_productos.html', {"Proyecto":nuevo_proyecto, "myFilter":myFilter, "productos_proyecto":productos_proyecto})

def guardar_datos_filtro(request):
    todos_productos = Producto.objects.all()
    id = request.GET["centro_costos"]
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
            nuevo_producto_proyecto=Producto_proyecto(id=uuid.uuid1(), producto=proyecto, proyecto=producto)
            nuevo_producto_proyecto.save()
            proyecto.save()
    productos_proyecto = proyecto.productos.all()
    productos = Filtro_producto.objects.all()
    myFilter = Filtro_productoFilter(request.GET, queryset=productos)
    producto = myFilter.qs
    return render(request, 'proyectos/eleccion_productos.html', {"Proyecto":proyecto, "myFilter":myFilter, "productos_proyecto":productos_proyecto})

#Recibir vista planificador I
def recibir_datos_planificador(request):
    proyecto = Proyecto.objects.get(id=request.GET["centro_costos"])
    productos_repetidos = request.GET.getlist("lista_productos")
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

def recibir_cantidades_planificador(request):
    numero_productos = int(request.GET["numero_productos"])
    proyecto = Proyecto.objects.get(id=request.GET["centro_costos"])
    lista_separada = []
    #Lista separada = Proveedores
    for i in range(numero_productos):
        a = request.GET.getlist("proveedor{}".format(str(i)))
        lista_separada.append(a)
    join = []
    for i in lista_separada:
        join += i
    proveedores = list(dict.fromkeys(join))
    cantidad = request.GET.getlist("cantidad")
    productos = request.GET.getlist("id_producto")
    lista_general_proveedores = []
    for proveedor in proveedores:
        lista_final = []
        lista_final.append(proveedor)
        nuevo_proveedor = Proveedor.objects.get(nombre=proveedor)
        lista_aux2 = []
        for counter, i in enumerate(lista_separada):
            lista_aux = []
            for k in i:
                if k == proveedor:
                    producto = Producto.objects.get(nombre=productos[int(counter)])
                    producto_proyecto = Producto_proyecto.objects.get(producto=proyecto, proyecto=producto)
                    #AGREGAMOS CANTIDAD Y PROVEEDORES.
                    producto_proyecto.cantidades = float(cantidad[counter])
                    producto_proyecto.proveedores.add(nuevo_proveedor)
                    producto_proyecto.save()
                    lista_aux.append(productos[int(counter)])
                    lista_aux.append(cantidad[counter])
                    lista_aux2.append(lista_aux)
        lista_final.append(lista_aux2)
        lista_final.append(nuevo_proveedor.contactos_asociados.all())
        lista_general_proveedores.append(lista_final)
    proyectos = Proyecto.objects.all()
    return render(request, "proyectos/proyectos.html", {"Proyectos":proyectos})

def agregar_cotizacion(request, id):
    if request.method == "POST":
        proyecto_asociado = Proyecto.objects.get(id=id)
        nombre = request.POST["nombre"]
        proveedor = request.POST["proveedor"]
        contacto = request.POST["contacto"]
        productos = request.POST.getlist("productos")
        contacto_asociado = Contacto.objects.get(nombre=contacto)
        proveedor_asociado = Proveedor.objects.get(nombre=proveedor)
        nueva_cotizacion = Cotizacion(id=uuid.uuid1(), nombre=nombre, proyecto_asociado=proyecto_asociado, proveedor_asociado = proveedor_asociado, contacto_asociado=contacto_asociado, fecha_salida = datetime.now())
        nueva_cotizacion.save()
        for i in productos:
            nuevo_producto = Producto.objects.get(nombre=i)
            nueva_cotizacion.productos_asociados.add(nuevo_producto)
            nueva_cotizacion.save()
        proyectos = Proyecto.objects.all()
        return render(request, "proyectos/proyectos.html", {"Proyectos":proyectos})
    else:
        proyecto = Proyecto.objects.get(id=id)
        productos = proyecto.productos.all()
        lista_proveedores = []
        lista_producto_proyecto = []
        for i in productos:
            producto_proyecto = Producto_proyecto.objects.filter(producto=proyecto, proyecto=i)
            lista_producto_proyecto.append(producto_proyecto)
            for n in producto_proyecto[0].proveedores.all():
                lista_proveedores.append(n.nombre)
        proveedores_no_repetidos =  list(dict.fromkeys(lista_proveedores))
        lista_proveedores_productos = []
        for i in lista_producto_proyecto:
            lista_aux = []
            for x in i[0].proveedores.all():
                lista_aux.append(x.nombre)
            lista_proveedores_productos.append(lista_aux)
        lista_final = []
        for proveedor in proveedores_no_repetidos:
            aux = []
            nuevo_proveedor = Proveedor.objects.get(nombre=proveedor)
            aux.append(nuevo_proveedor)
            aux2 = []
            for counter, i in enumerate(lista_proveedores_productos):
                booleano = False
                lista_aux = []
                for x in i:
                    if x == proveedor:
                        booleano = True
                if booleano:
                    lista_aux.append(lista_producto_proyecto[counter][0].proyecto.nombre)
                    lista_aux.append(lista_producto_proyecto[counter][0].cantidades)
                    lista_aux.append(lista_producto_proyecto[counter][0].proyecto.unidad)
                    lista_aux.append(lista_producto_proyecto[counter][0].fecha_uso)
                    aux2.append(lista_aux)
                    aux.append(aux2)
            lista_final.append(aux)
        lista_final_final = []
        for i in lista_final:
            lista_aux = []
            lista_aux.append(i[0])
            lista_aux.append(i[1])
            lista_final_final.append(lista_aux)
        return render(request, "proyectos/crear_cotizacion.html", {"Proyecto":proyecto, "Proveedores":lista_final_final})

def mostrar_cotizacion(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    return render(request, "proyectos/cotizacion.html", {"Cotizacion":cotizacion})

def editar_cotizacion(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    if request.method == "POST":
        cotizacion.nombre = request.POST["nombre"]
        cotizacion.fecha_respuesta = request.POST["fecha_respuesta"]
        cotizacion.save()
        proyectos = Proyecto.objects.all()
        return render(request, "proyectos/proyectos.html", {"Proyectos":proyectos})
    else:
        return render(request, "proyectos/editar_cotizacion.html", {"Cotizacion":cotizacion})
        
def eliminar_cotizacion(request, id):
    cotizacion = Cotizacion.objects.get(id=id)
    cotizacion.delete()
    proyectos = Proyecto.objects.all()
    return render(request, "proyectos/proyectos.html", {"Proyectos":proyectos})



"""
def enviar_correos(request):
    contactos = request.GET.getlist("contacto")
    numero_productos = request.GET.getlist("numero_productos")
    #numero_proveedores = request.GET.getlist("numero_proveedores")
    numero_contactos = request.GET.getlist("numero_contactos")
    productos = request.GET.getlist("productos")
    proveedores = request.GET.getlist("nombre")
    cantidades = request.GET.getlist("cantidades")
    #Lista de productos dependiendo de proveedores
    lista_productos = []
    contador_productos = 0
    for n, i in enumerate(numero_productos):
        lista_auxiliar_productos = []
        for n in range(int(i)):
            lista_aux = []
            lista_aux.append(productos[contador_productos])
            lista_aux.append(cantidades[contador_productos])
            unidad = Producto.objects.get(nombre=productos[contador_productos]).unidad
            lista_aux.append(unidad)
            lista_auxiliar_productos.append(lista_aux)
            contador_productos += 1
        lista_productos.append(lista_auxiliar_productos)
    #Lista de proveedores dependiendo de contacto.
    lista_proveedores = []
    contador_proveedores = 0
    for i in numero_contactos:
        for n in range(int(i)):
            lista_aux = []
            lista_aux.append(proveedores[contador_proveedores])
            lista_aux.append(lista_productos[contador_proveedores])
            lista_proveedores.append(lista_aux)
        contador_proveedores += 1
    for n, contacto in enumerate(contactos):
        lista_contactos = []
        lista_contactos.append(contacto)
        correo = Contacto.objects.get(nombre=contacto).correo
        lista_contactos.append(correo)
        lista_contactos.append(lista_proveedores[n][0])
        idioma = Proveedor.objects.get(nombre=lista_proveedores[n][0]).idioma
        lista_contactos.append(idioma)
        lista_contactos.append(lista_proveedores[n][1])
    #FALTA ENVIAR CORREO A PERSONAS REALES. ES COSA DE METER CONTENIDO_CORREO UN TAB ARRIBA.
    contenido_correo = crear_correo(lista_contactos)
        
    return HttpResponse("NO SE HA HECHO ESTA PARTE")
"""
