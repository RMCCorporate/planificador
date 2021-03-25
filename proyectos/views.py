from django.shortcuts import render
from planificador.models import Clase, SubClase, Producto, Proveedor, Contacto, Proyecto, Producto_proyecto, Precio
from planificador.filters import ProductoFilter
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
            for i in productos_proyecto[n].proveedores.all():
                auxiliar_proveedores.append(i)
                if i.nombre == precio.nombre_proveedor:
                    booleano_precio = True
        aux.append(producto_asociado)
        aux.append(sub_clase)
        aux.append(auxiliar_proveedores)
        if booleano_precio:
            aux.append(precio)
        else:
            aux.append(" ")
        productos.append(aux)
    return render(request, "proyectos/proyecto.html", {"Proyecto":proyecto, "Productos":productos_proyecto, "info_productos":productos})

def editar_precios(request, id):
    if request.method == "POST":
        proyecto = Proyecto.objects.get(id=id)
        id = request.POST.getlist("id")
        nombre = request.POST.getlist("nombre")
        valor = request.POST.getlist("valor")
        valor_importacion = request.POST.getlist("valor_importacion")
        tipo_cambio = request.POST.getlist("tipo_cambio")
        valor_cambio = request.POST.getlist("valor_cambio")
        fecha_uso = request.POST.getlist("fecha_uso")
        cantidades = request.POST.getlist("cantidades")
        proveedor = []
        status = []
        for i in nombre:
            proveedor.append(request.POST[i])
        for i in id:
            status.append(request.POST[str(i)])
        for n, producto in enumerate(id):
            producto = Producto.objects.get(id=producto)
            if valor[n] != "None":
                if valor_importacion[n] != "None":
                    if valor_cambio[n] == "None":
                        valor_cambio = 1
                    fecha_actual = datetime.now()
                    precio = Precio(id=uuid.uuid1(), valor=valor[n], valor_importación=valor_importacion[n], fecha=fecha_actual, tipo_cambio=tipo_cambio[n], valor_cambio=valor_cambio[n],  nombre_proveedor=proveedor[n])
                    precio.save()
                else:
                    fecha_actual = datetime.now()
                    precio = Precio(valor=valor[n], fecha=fecha_actual, nombre_proveedor=proveedor[n])
                    precio.save()
                producto.lista_precios.add(precio)
                producto.save()
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
        
        #Renderizar
        proyectos = Proyecto.objects.all()
        return render(request, "proyectos/proyectos.html", {"Proyectos":proyectos})
    else:
        proyecto = Proyecto.objects.get(id=id)
        a = Precio.objects.all()
        for i in a:
            i.delete()
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

def recibir_edicion(request):
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
    productos = Producto.objects.all()
    myFilter = ProductoFilter(request.GET, queryset=productos)
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
            nuevo_producto_proyecto=Producto_proyecto(producto=proyecto, proyecto=producto)
            nuevo_producto_proyecto.save()
            proyecto.save()
    productos_proyecto = proyecto.productos.all()
    myFilter = ProductoFilter(request.GET, queryset=todos_productos)
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

    return render(request, "proyectos/lista_proveedores.html", {"Productos":lista_general_proveedores})

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