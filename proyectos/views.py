from django.shortcuts import render
from planificador.models import Clase, SubClase, Producto, Proveedor, Contacto
from django.http import HttpResponse

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

#Recibir vista planificador I
def recibir_datos_planificador(request):
    id = request.GET["id"]
    nombre = request.GET["nombre"]
    tipo_cambio = request.GET["tipo_cambio"]
    valor_cambio = request.GET["valor_cambio"]
    fecha_inicio = request.GET["fecha_inicio"]
    fecha_termino = request.GET["fecha_termino"]
    productos = request.GET.getlist("subclase")
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
    return render(request, "proyectos/lista_productos.html", {"Productos":lista_subclases_productos})

def recibir_cantidades_planificador(request):
    numero_productos = int(request.GET["numero_productos"])
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
    lista_final_final = []
    for proveedor in proveedores:
        lista_final = []
        lista_final.append(proveedor)
        nuevo_proveedor = Proveedor.objects.get(nombre=proveedor)
        lista_aux2 = []
        for counter, i in enumerate(lista_separada):
            lista_aux = []
            for k in i:
                if k == proveedor:
                    lista_aux.append(productos[int(counter)])
                    lista_aux.append(cantidad[counter])
                    lista_aux2.append(lista_aux)
        lista_final.append(lista_aux2)
        lista_final.append(nuevo_proveedor.contactos_asociados.all())
        lista_general_proveedores.append(lista_final)
    lista_correos = []
    for i in proveedores:
        nuevo_proveedor = Proveedor.objects.get(nombre=i)
    return render(request, "proyectos/lista_proveedores.html", {"Productos":lista_general_proveedores})

def enviar_correos(request):
    contactos = request.GET.getlist("contacto")
    numero_productos = request.GET.getlist("numero_productos")
    numero_proveedores = request.GET.getlist("numero_proveedores")
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
        contenido_correo = crear_correo(lista_contactos)
        #FALTA ENVIAR CORREO
    
    return HttpResponse("NO SE HA HECHO ESTA PARTE")