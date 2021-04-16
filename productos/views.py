from django.shortcuts import render
from django.http import HttpResponse
from planificador.models import Producto, Clase, SubClase, Precio, Filtro_producto
from datetime import date, datetime
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth.decorators import login_required
from django import forms
import openpyxl

class UploadFileForm(forms.Form):
    file = forms.FileField()

class ImageForm(forms.ModelForm):
    """Form for the image model"""
    class Meta:
        model = Producto
        fields = ('id', 'nombre', 'unidad', 'kilos', 'imagen')

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

#Mostrar productos
@login_required(login_url='/login')
def productos(request):
    productos = Producto.objects.all()
    if request.method == "POST":
        datos_fallados = []
        booleano_fallados = False
        excel_file = request.FILES["excel_file"]
        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb["producto"]
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            id = row_data[0].upper()
            nombre = row_data[1].upper()
            unidad = row_data[2].upper()
            kilos = row_data[3].upper()
            subclase = row_data[4].upper()
            if id != "ID":
                if id == "NONE" or nombre == "NONE":
                    aux = []
                    aux.append(row_data[0])
                    aux.append(row_data[1])
                    aux.append("No se ingresó ID o Nombre")
                    datos_fallados.append(aux)
                else:
                    fecha_actualizacion = datetime.now()
                    if Producto.objects.filter(id=id).exists():
                        aux = []
                        aux.append(row_data[0])
                        aux.append(row_data[1])
                        aux.append("Producto con id:{} ya existe".format(id))
                        datos_fallados.append(aux)
                    else:
                        if not SubClase.objects.filter(nombre=subclase).exists():
                            aux = []
                            aux.append(row_data[0])
                            aux.append(row_data[1])
                            aux.append("La SubClase {} no existe".format(subclase))
                            datos_fallados.append(aux)
                        else:
                            nuevo_producto = Producto(id=id, nombre=nombre, fecha_actualizacion=fecha_actualizacion)
                            if unidad != "None":
                                nuevo_producto.unidad = unidad
                            if kilos != "None":
                                es_float = isfloat(kilos)
                                if es_float:
                                    nuevo_producto.kilos = kilos
                                else:
                                    aux = []
                                    aux.append(row_data[0])
                                    aux.append(row_data[1])
                                    aux.append("Producto creado sin kilos. No es un número")
                                    datos_fallados.append(aux)
                            nuevo_producto.save()
                            sub_clase = SubClase.objects.get(nombre=subclase)
                            sub_clase.productos.add(nuevo_producto)
                            clase = sub_clase.clase_set.all()
                            nuevo_filtro_producto = Filtro_producto(nombre_producto=nombre, nombre_clase=clase[0].nombre, nombre_subclase=subclase)
                            nuevo_filtro_producto.save()
                            sub_clase.save()
        if len(datos_fallados)!=0:
            booleano_fallados = True
        return render(request, 'productos/resultado_planilla_productos.html', {"Fallo":datos_fallados, "Booleano":booleano_fallados})
    return render(request, "productos/productos.html", {"Productos":productos})

#Agregar producto
@login_required(login_url='/login')
def agregar_producto(request):
    clases = Clase.objects.all()
    subclases = SubClase.objects.all()
    return render(request, "productos/crear_producto.html", {"Clases":clases, "Subclases":subclases})


def recibir_datos_producto(request):
    id = request.GET["id"]
    nombre = request.GET["nombre"]
    sub_clase = request.GET["subclase"]
    unidad = request.GET["unidad"]
    nuevo_producto = Producto(id=id, nombre=nombre, unidad=unidad)
    nuevo_producto.save()
    subclase = SubClase.objects.get(nombre=sub_clase)
    subclase.productos.add(nuevo_producto)
    clase = subclase.clase_set.all()
    nuevo_filtro_producto = Filtro_producto(nombre_producto=nombre, nombre_clase=clase[0].nombre, nombre_subclase=subclase.nombre)
    nuevo_filtro_producto.save()
    productos = Producto.objects.all()
    return render(request, "productos/productos.html", {"Productos":productos})
   
#Vista producto
@login_required(login_url='/login')
def producto(request, id):
    producto = Producto.objects.get(id=id)
    lista_precios = producto.lista_precios.all()
    a = lista_precios.order_by('-fecha')
    sub_clase = producto.subclase_set.all()[0]
    clase = sub_clase.clase_set.all()[0]
    return render(request, "productos/producto.html", {"Producto":producto, "lista_precios":a, "Subclase":sub_clase, "Clase":clase})

#Edición producto
@login_required(login_url='/login')
def mostrar_edicion_producto(request, id):
    producto = Producto.objects.get(id=id)
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            # Get the current instance object to display in the template
            img_obj = form.instance
            productos = Producto.objects.all()
            return render(request, 'productos/productos.html', {'Productos': productos})
    else:
        subclases = SubClase.objects.all()
        form = ImageForm(instance=producto)
        return render(request, "productos/editar_producto.html", {"Producto":producto, "Subclases":subclases, "form":form})

@login_required(login_url='/login')
def editar_precio_producto(request, id):
    producto = Producto.objects.get(id=id)
    precio = request.POST["precio"]
    if precio != "":
        precio = 0
        moneda = request.POST["moneda"]
        proveedor = request.POST["proveedor"]
        comentario = request.POST["comentario"]
        nuevo_precio = Precio(id=producto.id, valor=precio, tipo_cambio=moneda, nombre_proveedor=proveedor, comentarios=comentario)
        nuevo_precio.save()
        producto.lista_precios.add(nuevo_precio)
        producto.save()

#Eliminar producto
@login_required(login_url='/login')
def eliminar_producto(request, id):
    producto = Producto.objects.get(id=id)
    producto.delete()
    productos = Producto.objects.all()
    return render(request, "productos/productos.html", {"Productos":productos})
