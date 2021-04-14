from django.shortcuts import render, redirect
from planificador.models import Producto, SubClase, Proveedor, Clase
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from planificador.decorators import allowed_users
import openpyxl

# Create your views here.
@login_required(login_url='/login')
def index(request):
    #group = str(request.user.groups.all()[0])
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

@allowed_users(allowed_roles=['Admin'])
@login_required(login_url='/login')
def crear_usuario(request):
    if request.method == "POST":
        nickname = request.POST["nickname"]
        nombre = request.POST["nombre"]
        apellido = request.POST["apellido"]
        correo = request.POST["correo"]
        contraseña = request.POST["contraseña"]
        nombre_grupo = request.POST["grupo"]
        nuevo_usuario = User.objects.create_user(nickname, correo, contraseña)
        nuevo_usuario.first_name = nombre
        nuevo_usuario.last_name = apellido
        nuevo_usuario.save()
        grupo = Group.objects.get(name=nombre_grupo)
        nuevo_usuario.groups.add(grupo)
        nuevo_usuario.save()
        return redirect('/')
    else:
        return render(request, 'planificador/crear_usuario.html')

@allowed_users(allowed_roles=['Admin'])
@login_required(login_url='/login')
def crear_grupo(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]
        usuario = request.POST["usuario"]
        if not Group.objects.filter(name=str(nombre)).exists():
            nuevo_grupo = Group.objects.create(name=nombre)
            nuevo_grupo.save()
            usuario = User.objects.get(username=usuario)
            print(usuario.first_name)
            usuario.groups.add(nuevo_grupo)
            usuario.save()
        else:
            grupo = Group.objects.get(name=nombre)
            print(usuario)
            usuario = User.objects.get(username=usuario)
            usuario.groups.add(grupo)
            usuario.save()
        return redirect('/')
    else:
        usuarios = User.objects.all()
        return render(request, 'planificador/crear_grupo.html', {'usuarios':usuarios})




    
    