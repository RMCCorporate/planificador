from django.shortcuts import render, redirect
from planificador.models import (
    SubClase,
    Clase,
    Permisos_notificacion,
    Notificacion,
    Planilla,
)
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
import openpyxl
from django.contrib.auth import get_user_model


def takedate(elem):
    return elem.fecha


@login_required(login_url="/login")
def notificaciones(request):
    permisos_notificacion = Permisos_notificacion.objects.filter(
        usuarios__correo=request.user.correo
    )
    for i in permisos_notificacion:
        notificaciones = Notificacion.objects.filter(tipo=i.nombre)
        lista_notificaciones = [i for i in notificaciones if i]
    lista_notificaciones.sort(key=takedate)
    lista_notificaciones.reverse()
    usuario = get_user_model().objects.get(correo=request.user.correo)
    payload = {"notificacion": lista_notificaciones, "usuario": usuario}
    return render(request, "planificador/notificaciones.html", payload)


@login_required(login_url="/login")
def index(request):
    usuario = str(request.user.groups.all()[0]) if request.user.groups.all() else "Admin"
    planilla = Planilla.objects.get(id="0").planilla if Planilla.objects.filter(id="0").exists() else False
    payload = {"rol": usuario, "planilla": planilla}
    return render(request, "planificador/index.html", payload)


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
        return redirect("/")
    else:
        return render(request, "planificador/actualizar_planilla.html")


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
                if not (row_data[0] == "None" and row_data[1] == "None"):
                    aux = [row_data[0], row_data[1], "No se ingresó Subclase o Clase"]
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
                        nueva_clase = Clase(nombre=dato_clase)
                        nueva_clase.save()
                        nueva_subclase = SubClase(nombre=dato_subclase)
                        nueva_subclase.save()
                        nueva_clase.subclases.add(nueva_subclase)
                        nueva_clase.save()
        if len(datos_fallados) != 0:
            booleano_fallados = True
        payload = {"Fallo": datos_fallados, "Booleano": booleano_fallados}
        return render(request, "planificador/resultado_planilla.html", payload)
    else:
        return render(request, "planificador/nueva_subclase.html")


# @allowed_users(allowed_roles=['Admin'])
@login_required(login_url="/login")
def crear_usuario(request):
    if request.method == "POST":
        post = request.POST
        if get_user_model().objects.filter(correo=post["correo"]).exists():
            nuevo_usuario = get_user_model().objects.get(correo=post["correo"])
        else:
            nuevo_usuario = get_user_model().objects.create_user(post["correo"], post["contraseña"])
        nuevo_usuario.nombre = post["nombre"]
        nuevo_usuario.nickname = post["nickname"]
        nuevo_usuario.apellido = post["apellido"]
        nuevo_usuario.segundo_apellido = post["segundo_apellido"]
        nuevo_usuario.celular = post["celular"]
        nuevo_usuario.cargo = post["cargo"]
        nuevo_usuario.telefono = post["telefono"]
        nuevo_usuario.notificaciones = 0
        nuevo_usuario.save()
        grupo = Group.objects.get(name=post["grupo"])
        nuevo_usuario.groups.add(grupo)
        nuevo_usuario.save()
        permisos = [
            "editar_precio",
            "editar_producto_proyecto",
            "eliminar_producto_proyecto",
            "agregar_producto_proyecto",
            "crear_proyecto",
            "crear_cotizacion",
            "editar_fecha_respuesta_cotización",
            "eliminar_cotización",
            "enviar_correo",
            "agregar_proveedor",
            "editar_proveedor",
            "eliminar_contacto",
            "eliminar_proveedor",
            "agregar_producto",
            "editar_producto",
            "eliminar_producto",
        ]
        for i in permisos:
            permiso = Permisos_notificacion.objects.get(nombre=i)
            permiso.usuarios.add(nuevo_usuario)
            permiso.save()
        return redirect("/")
    else:
        return render(request, "planificador/crear_usuario.html")


# @allowed_users(allowed_roles=['Admin'])
@login_required(login_url="/login")
def crear_grupo(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]
        usuario = request.POST["usuario"]
        if not Group.objects.filter(name=str(nombre)).exists():
            nuevo_grupo = Group.objects.create(name=nombre)
            nuevo_grupo.save()
            usuario = get_user_model().objects.get(correo=str(request.user.correo))
            usuario.groups.add(nuevo_grupo)
            usuario.save()
        else:
            grupo = Group.objects.get(name=nombre)
            usuario = get_user_model().objects.get(correo=str(request.user.correo))
            usuario.groups.add(grupo)
            usuario.save()
        return redirect("/")
    else:
        usuarios = get_user_model().objects.all()
        return render(request, "planificador/crear_grupo.html", {"usuarios": usuarios})


# @allowed_users(allowed_roles=['Admin'])
@login_required(login_url="/login")
def crear_permisos(request):
    permisos = [
        "editar_precio",
        "editar_producto_proyecto",
        "eliminar_producto_proyecto",
        "agregar_producto_proyecto",
        "crear_proyecto",
        "crear_cotizacion",
        "editar_fecha_respuesta_cotización",
        "eliminar_cotización",
        "enviar_correo",
        "agregar_proveedor",
        "editar_proveedor",
        "eliminar_contacto",
        "eliminar_proveedor",
        "agregar_producto",
        "editar_producto",
        "eliminar_producto",
    ]
    for i in permisos:
        nuevo_permiso = Permisos_notificacion(nombre=i)
        nuevo_permiso.save()
    return redirect("/")


@login_required(login_url="/login")
def permisos_notificacion(request):
    if request.method == "POST":
        usuario = get_user_model().objects.get(correo=request.user.correo)
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
        return redirect("/")
    else:
        permisos = Permisos_notificacion.objects.all()
        lista_con = []
        lista_sin = []
        for i in permisos:
            con = False
            for x in i.usuarios.all():
                if x.correo == request.user.correo:
                    con = True
            if con:
                lista_con.append(i.nombre)
            else:
                lista_sin.append(i.nombre)
        lista_ordenada = [["PRODUCTO"], ["PROYECTO"], ["COTIZACIÓN"], ["PROVEEDOR"]]
        for i in lista_con:
            if i[-4:] == "ucto":
                aux = ["Si", i]
                if i[:3] == "agr":
                    aux.append("Agregar")
                elif i[:3] == "edi":
                    aux.append("Editar")
                elif i[:3] == "eli":
                    aux.append("Eliminar")
                lista_ordenada[0].append(aux)
            elif i[-4:] == "ecto":
                aux = ["Si", i]
                if i[:3] == "cre":
                    aux.append("Crear proyecto")
                elif i[:3] == "agr":
                    aux.append("Agregar producto en proyecto")
                elif i[:3] == "edi":
                    aux.append("Editar producto en proyecto")
                elif i[:3] == "eli":
                    aux.append("Eliminar producto en proyecto")
                lista_ordenada[1].append(aux)
            elif (
                i[-4:] == "ción"
                or i[-4:] == "cion"
                or i[-4:] == "rreo"
                or i[-4:] == "ecio"
            ):
                aux = ["Si", i]
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
                aux = ["Si", i]
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
                aux = ["No", i]
                if i[:3] == "agr":
                    aux.append("Agregar")
                elif i[:3] == "edi":
                    aux.append("Editar")
                elif i[:3] == "eli":
                    aux.append("Eliminar")
                lista_ordenada[0].append(aux)
            elif i[-4:] == "ecto":
                aux = ["No", i]
                if i[:3] == "cre":
                    aux.append("Crear proyecto")
                elif i[:3] == "agr":
                    aux.append("Agregar producto en proyecto")
                elif i[:3] == "edi":
                    aux.append("Editar producto en proyecto")
                elif i[:3] == "eli":
                    aux.append("Eliminar producto en proyecto")
                lista_ordenada[1].append(aux)
            elif (
                i[-4:] == "ción"
                or i[-4:] == "cion"
                or i[-4:] == "rreo"
                or i[-4:] == "ecio"
            ):
                aux = ["No", i]
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
                aux = ["No", i]
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
            lista = [x for x in i if type(x) == list]
            lista_final.append([i[0], lista])
        payload = {"con": lista_con, "sin": lista_sin, "lista_ordenada": lista_final}
        return render(request, "planificador/permisos_notificacion.html", payload)


@login_required(login_url="/login")
def usuario(request):
    usuario = get_user_model().objects.get(correo=str(request.user.correo))
    lista_precios = usuario.precios.all()
    Productos = usuario.productos_proyecto.all()
    Proyectos = usuario.proyectos.all()
    cotizaciones = usuario.cotizaciones.all()
    payload = {
        "Usuario": usuario,
        "lista_precios": lista_precios,
        "Productos": Productos,
        "Proyectos": Proyectos,
        "cotizaciones": cotizaciones,
    }
    return render(request, "planificador/usuario.html", payload)


@login_required(login_url="/login")
def editar_usuario(request, correo):
    if request.method == "POST":
        post = request.POST
        usuario = get_user_model().objects.get(correo=correo)
        usuario.nombre = post["nombre"]
        usuario.apellido = post["apellido"]
        usuario.segundo_apellido = post["segundo_apellido"]
        usuario.cargo = post["cargo"]
        usuario.celular = post["celular"]
        usuario.telefono = post["telefono"]
        usuario.save()
        return redirect("/planificador/usuario/")
    else:
        usuario = get_user_model().objects.get(correo=str(request.user.correo))
        payload = {"Usuario": usuario}
        return render(request, "planificador/editar_usuario.html", payload)
