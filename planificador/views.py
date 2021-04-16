from django.shortcuts import render, redirect
from planificador.models import Producto, SubClase, Proveedor, Clase, Usuario
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from planificador.decorators import allowed_users
import openpyxl

# Create your views here.
@login_required(login_url='/login')
def index(request):
    #group = str(request.user.groups.all()[0])
    if request.method == "POST":
        datos_fallados = []
        booleano_fallados = False
        excel_file = request.FILES["excel_file"]
        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb["subclase"]
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            if row_data[0] == "None" or row_data[1] == "None":
                aux = []
                aux.append(row_data[0])
                aux.append(row_data[1])
                aux.append("No se ingresó Subclase o Clase")
                datos_fallados.append(aux)
            else:
                dato_subclase = row_data[0].upper()
                dato_clase = row_data[1].upper()
                if dato_subclase != "NOMBRE":
                    if Clase.objects.filter(nombre=dato_clase).exists():
                        if SubClase.objects.filter(nombre=dato_subclase).exists():
                            aux = []
                            aux.append(row_data[0])
                            aux.append(row_data[1])
                            aux.append("Subclase ya existe")
                            datos_fallados.append(aux)
                        else:
                            nueva_subclase = SubClase(nombre=dato_subclase)
                            nueva_subclase.save()
                            clase = Clase.objects.get(nombre=dato_clase)
                            clase.subclases.add(nueva_subclase)
                            clase.save()
                    else:
                        aux = []
                        aux.append(row_data[0])
                        aux.append(row_data[1])
                        aux.append("Clase no encontrada")
                        datos_fallados.append(aux)
        if len(datos_fallados)!=0:
            booleano_fallados = True
        return render(request, 'planificador/resultado_planilla.html', {"Fallo":datos_fallados, "Booleano":booleano_fallados})
                
    return render(request, 'planificador/index.html')

#@allowed_users(allowed_roles=['Admin'])
@login_required(login_url='/login')
def crear_usuario(request):
    if request.method == "POST":
        nickname = request.POST["nickname"]
        nombre = request.POST["nombre"]
        apellido = request.POST["apellido"]
        segundo_apellido = request.POST["segundo_apellido"]
        cargo = request.POST["cargo"]
        celular = request.POST["celular"]
        telefono = request.POST["telefono"]
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
        usuario_info = Usuario(correo=correo, nombre=nombre, apellido=apellido, segundo_apellido=segundo_apellido, celular=celular, cargo=cargo, telefono=telefono)
        usuario_info.save()
        return redirect('/')
    else:
        return render(request, 'planificador/crear_usuario.html')

#@allowed_users(allowed_roles=['Admin'])
@login_required(login_url='/login')
def crear_grupo(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]
        usuario = request.POST["usuario"]
        if not Group.objects.filter(name=str(nombre)).exists():
            nuevo_grupo = Group.objects.create(name=nombre)
            nuevo_grupo.save()
            usuario = User.objects.get(username=usuario)
            usuario.groups.add(nuevo_grupo)
            usuario.save()
        else:
            grupo = Group.objects.get(name=nombre)
            usuario = User.objects.get(username=usuario)
            usuario.groups.add(grupo)
            usuario.save()
        return redirect('/')
    else:
        usuarios = User.objects.all()
        return render(request, 'planificador/crear_grupo.html', {'usuarios':usuarios})


@login_required(login_url='/login')
def usuario(request):
    print(request.user.email)
    usuario = Usuario.objects.get(correo=str(request.user.email))
    return render(request, 'planificador/usuario.html', {'Usuario':usuario})

@login_required(login_url='/login')
def editar_usuario(request, correo):
    if request.method == "POST":
        usuario = Usuario.objects.get(correo=correo)
        usuario.nombre = request.POST["nombre"]
        usuario.apellido = request.POST["apellido"]
        usuario.segundo_apellido = request.POST["segundo_apellido"]
        usuario.cargo = request.POST["cargo"]
        usuario.celular = request.POST["celular"]
        usuario.telefono = request.POST["telefono"]
        usuario.save()
        return redirect('/planificador/usuario/')
    else:
        usuario = Usuario.objects.get(correo=str(request.user.email))
        return render(request, 'planificador/editar_usuario.html', {'Usuario':usuario})
