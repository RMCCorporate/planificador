from django.shortcuts import render, redirect
from planificador.models import Producto, SubClase, Proveedor, Clase, Usuario, Permisos_notificacion, Notificacion, Planilla
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from planificador.decorators import allowed_users
import openpyxl
import uuid


# Create your views here.
def takedate(elem):
    return elem.fecha

@login_required(login_url='/login')
def notificaciones(request):
    lista_notificaciones = []
    permisos_notificacion = Permisos_notificacion.objects.filter(usuarios__correo=request.user.email)
    for i in permisos_notificacion:
        notificaciones = Notificacion.objects.filter(tipo=i.nombre)
        for i in notificaciones:
            if i:
                lista_notificaciones.append(i)
    lista_notificaciones.sort(key=takedate)
    lista_notificaciones.reverse()
    usuario = Usuario.objects.get(correo=request.user.email)
    return render(request, 'planificador/notificaciones.html', {'notificacion':lista_notificaciones, 'usuario':usuario})

@login_required(login_url='/login')
def index(request):
    usuario = str(request.user.groups.all()[0])
    if Planilla.objects.filter(id="0").exists():
        planilla = Planilla.objects.get(id="0").planilla
    else:
        planilla = False
    return render(request, 'planificador/index.html', {"rol":usuario, "planilla":planilla})

def actualizar_planilla(request):
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        if not Planilla.objects.filter(id="0").exists():
            nueva_planilla = Planilla(id="0", planilla=excel_file)
            nueva_planilla.save()
        else:
            nueva_planilla = Planilla.objects.get(id="0")
            nueva_planilla.planilla = excel_file
            nueva_planilla.save()
        return redirect('/')
    else:
        return render(request, 'planificador/actualizar_planilla.html')

def agregar_subclases(request):
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
                if not(row_data[0] == "None" and row_data[1] == "None"):
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
                            subclase_nueva = SubClase.objects.get(nombre=dato_subclase)
                            clase = Clase.objects.get(nombre=dato_clase)
                            clase.subclases.add(subclase_nueva)
                            clase.save()
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
    else:
        return render(request, 'planificador/nueva_subclase.html')  

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
        usuario_info = Usuario(correo=correo, nickname=nickname, nombre=nombre, apellido=apellido, segundo_apellido=segundo_apellido, celular=celular, cargo=cargo, telefono=telefono, notificaciones=0)
        usuario_info.save()
        permisos = ["editar_precio", "editar_producto_proyecto", "eliminar_producto_proyecto", "agregar_producto_proyecto", "crear_proyecto", "crear_cotizacion","editar_fecha_respuesta_cotización", "eliminar_cotización", "enviar_correo","agregar_proveedor", "editar_proveedor", "eliminar_contacto", "eliminar_proveedor", "agregar_producto", "editar_producto", "eliminar_producto"]
        for i in permisos:
            permiso = Permisos_notificacion.objects.get(nombre=i)
            permiso.usuarios.add(usuario_info)
            permiso.save()
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

#@allowed_users(allowed_roles=['Admin'])
@login_required(login_url='/login')
def crear_permisos(request):
    permisos = ["editar_precio", "editar_producto_proyecto", "eliminar_producto_proyecto", "agregar_producto_proyecto", "crear_proyecto", "crear_cotizacion","editar_fecha_respuesta_cotización", "eliminar_cotización", "enviar_correo","agregar_proveedor", "editar_proveedor", "eliminar_contacto", "eliminar_proveedor", "agregar_producto", "editar_producto", "eliminar_producto"]
    for i in permisos:
        nuevo_permiso = Permisos_notificacion(nombre=i)
        nuevo_permiso.save()
    return redirect('/')
  
@login_required(login_url='/login')
def permisos_notificacion(request):
    if request.method == "POST":
        usuario = Usuario.objects.get(correo=request.user.email)
        todos_los_permisos = Permisos_notificacion.objects.all()
        for n in todos_los_permisos:
            for j in n.usuarios.all():
                if j == usuario:
                    n.usuarios.remove(j)
        permisos = request.POST.getlist("permiso")
        for i in permisos:
            permiso = Permisos_notificacion.objects.get(nombre=i)
            permiso.usuarios.add(usuario)
            permiso.save()
        return redirect('/')
    else:
        permisos = Permisos_notificacion.objects.all()
        lista_con = []
        lista_sin = []
        for i in permisos:
            con = False
            for x in i.usuarios.all():
                if x.correo == request.user.email:
                    con = True
            if con:
                lista_con.append(i.nombre)
            else:
                lista_sin.append(i.nombre)
        lista_ordenada = [["PRODUCTO"], ["PROYECTO"], ["COTIZACIÓN"], ["PROVEEDOR"]]
        for i in lista_con:
            if i[-4:] == "ucto":
                aux = []
                aux.append("Si")
                aux.append(i)
                if i[:3] == "agr":
                    aux.append("Agregar")
                elif i[:3] == "edi":
                    aux.append("Editar")
                elif i[:3] == "eli":
                    aux.append("Eliminar")
                lista_ordenada[0].append(aux)
            elif i[-4:] == "ecto":
                aux = []
                aux.append("Si")
                aux.append(i)
                if i[:3] == "cre":
                    aux.append("Crear proyecto")
                elif i[:3] == "agr":
                    aux.append("Agregar producto en proyecto")
                elif i[:3] == "edi":
                    aux.append("Editar producto en proyecto")
                elif i[:3] == "eli":
                    aux.append("Eliminar producto en proyecto")
                lista_ordenada[1].append(aux)
            elif i[-4:] ==  "ción" or i[-4:] ==  "cion" or i[-4:] == "rreo" or i[-4:] == "ecio":
                aux = []
                aux.append("Si")
                aux.append(i)
                if i[:3] == "cre":
                    aux.append("Crear cotización")
                elif i[:3] == "env":
                    aux.append("Enviar correo de cotización")
                elif i[:8] == "editar_f":
                    aux.append("Editar fecha respuesta de cotización")
                elif i[:8] == "editar_p":
                    aux.append("Agregar precio de productos en cotización")
                elif i[:3] == "eli":
                    aux.append("Eliminar cotización de proyecto")
                lista_ordenada[2].append(aux)
            elif i[-4:] == "edor" or i[-4:] == "acto":
                aux = []
                aux.append("Si")
                aux.append(i)
                if i[:3] == "agr":
                    aux.append("Agregar")
                elif i[:3] == "edi":
                    aux.append("Editar")
                elif i[:10] == "eliminar_c":
                    aux.append("Eliminar contacto")
                elif i[:3] == "eliminar_p":
                    aux.append("Eliminar proveedor")
                lista_ordenada[3].append(aux)
        for i in lista_sin:
            if i[-4:] == "ucto":
                aux = []
                aux.append("No")
                aux.append(i)
                if i[:3] == "agr":
                    aux.append("Agregar")
                elif i[:3] == "edi":
                    aux.append("Editar")
                elif i[:3] == "eli":
                    aux.append("Eliminar")
                lista_ordenada[0].append(aux)
            elif i[-4:] == "ecto":
                aux = []
                aux.append("No")
                aux.append(i)
                if i[:3] == "cre":
                    aux.append("Crear proyecto")
                elif i[:3] == "agr":
                    aux.append("Agregar producto en proyecto")
                elif i[:3] == "edi":
                    aux.append("Editar producto en proyecto")
                elif i[:3] == "eli":
                    aux.append("Eliminar producto en proyecto")
                lista_ordenada[1].append(aux)
            elif i[-4:] ==  "ción" or i[-4:] ==  "cion" or i[-4:] == "rreo" or i[-4:] == "ecio":
                aux = []
                aux.append("No")
                aux.append(i)
                if i[:3] == "cre":
                    aux.append("Crear cotización")
                elif i[:3] == "env":
                    aux.append("Enviar correo de cotización")
                elif i[:8] == "editar_f":
                    aux.append("Editar fecha respuesta de cotización")
                elif i[:8] == "editar_p":
                    aux.append("Agregar precio de productos en cotización")
                elif i[:3] == "eli":
                    aux.append("Eliminar cotización de proyecto")
                lista_ordenada[2].append(aux)
            elif i[-4:] == "edor" or i[-4:] == "acto":
                aux = []
                aux.append("No")
                aux.append(i)
                if i[:3] == "agr":
                    aux.append("Agregar")
                elif i[:3] == "edi":
                    aux.append("Editar")
                elif i[:10] == "eliminar_c":
                    aux.append("Eliminar contacto")
                elif i[:10] == "eliminar_p":
                    aux.append("Eliminar proveedor")
                lista_ordenada[3].append(aux)
        lista_final = []
        for i in lista_ordenada:
            lista = []
            for x in i:
                if type(x) == list:
                    lista.append(x)
            aux = []
            aux.append(i[0])
            aux.append(lista)
            lista_final.append(aux)
            #print(lista_ordenada)
        return render(request, 'planificador/permisos_notificacion.html', {'con':lista_con, 'sin':lista_sin, "lista_ordenada":lista_final})
    
@login_required(login_url='/login')
def usuario(request):
    usuario = Usuario.objects.get(correo=str(request.user.email))
    lista_precios = usuario.precios.all()
    Productos = usuario.productos_proyecto.all()
    Proyectos = usuario.proyectos.all()
    cotizaciones = usuario.cotizaciones.all()
    return render(request, 'planificador/usuario.html', {'Usuario':usuario, "lista_precios":lista_precios, "Productos":Productos, "Proyectos":Proyectos, "cotizaciones":cotizaciones})

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
