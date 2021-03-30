from django.shortcuts import render
from django.http import HttpResponse
from planificador.models import Producto, Clase, SubClase, Precio
from datetime import date, datetime
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django import forms
import openpyxl

class UploadFileForm(forms.Form):
    file = forms.FileField()

class ImageForm(forms.ModelForm):
    """Form for the image model"""
    class Meta:
        model = Producto
        fields = ('id', 'nombre', 'unidad', 'kilos', 'imagen')

#Mostrar productos
def productos(request):
    productos = Producto.objects.all()
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb["producto"]
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            if row_data[0] != "id":
                fecha_actualizacion = datetime.now()
                nuevo_producto = Producto(id=row_data[0], nombre=row_data[1], fecha_actualizacion=fecha_actualizacion, unidad=row_data[2], kilos=row_data[3])
                nuevo_producto.save()
                sub_clase = SubClase.objects.get(nombre=row_data[4])
                sub_clase.productos.add(nuevo_producto)
                sub_clase.save()
    return render(request, "productos/productos.html", {"Productos":productos})

#Agregar producto
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
    productos = Producto.objects.all()
    return render(request, "productos/productos.html", {"Productos":productos})
   
#Vista producto
def producto(request, id):
    producto = Producto.objects.get(id=id)
    lista_precios = producto.lista_precios.all()
    a = lista_precios.order_by('-fecha')
    sub_clase = producto.subclase_set.all()[0]
    clase = sub_clase.clase_set.all()[0]
    return render(request, "productos/producto.html", {"Producto":producto, "lista_precios":a, "Subclase":sub_clase, "Clase":clase})

#Edición producto
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
def eliminar_producto(request, id):
    producto = Producto.objects.get(id=id)
    producto.delete()
    productos = Producto.objects.all()
    return render(request, "productos/productos.html", {"Productos":productos})
