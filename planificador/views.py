from django.shortcuts import render
from planificador.models import Producto, SubClase, Proveedor, Clase
import openpyxl

# Create your views here.
def index(request):
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb["subclase"]
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            if row_data[0] != "nombre":
                nueva_subclase = SubClase(nombre=row_data[0])
                nueva_subclase.save()
                productos = row_data[1]
                productos_repartidos = productos.split(',')
                for i in productos_repartidos:
                    producto = Producto.objects.get(id=i)
                    nueva_subclase.productos.add(producto)
                proveedores = row_data[2]
                proveedores_repartidos = proveedores.split(',')
                for i in proveedores_repartidos:
                    proveedor = Proveedor.objects.get(nombre=i)
                    proveedor.subclases_asociadas.add(nueva_subclase)
                    proveedor.save()
                clase = row_data[3]
                clase = Clase.objects.get(nombre=clase)
                clase.subclases.add(nueva_subclase)
                clase.save()

    return render(request, 'planificador/index.html')