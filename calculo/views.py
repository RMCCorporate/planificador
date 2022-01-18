from django.shortcuts import render
from django.shortcuts import render, redirect
from planificador.models import (
    Atributo,
    Calculo,
    ControlRiesgo,
    Instalaciones,
    Precio,
    Producto,
    Producto_proyecto_cantidades,
    Restricciones,
    InstalacionProyecto
)
from planificador.filters import (
    Filtro_productoFilter,
)
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from planificador.filters import Filtro_producto
from planificador.decorators import allowed_users
import openpyxl
import uuid
import json
import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from django.contrib.auth import get_user_model
import math
import re


def calculo_parentesis(formula, lista):
    if "(" not in formula:
        return lista
    else:
        if len(lista) == 0:
            lista.append(formula)
        parentesis = formula[formula.find("(")+1:formula.rfind(")")]
        lista.append(parentesis)
        return calculo_parentesis(parentesis, lista)

def lista_abreviaciones(formula):
    lista = []
    if "int" in formula:
        formula_sin_int = formula.split("int")
        for i in formula_sin_int:
            for x in i:
                if x.isalpha():
                    lista.append(x)
    else:
        for i in formula:
            if i.isalpha():
                lista.append(i)
    return list(dict.fromkeys(lista))

def operador(valor1, operador, valor2):
    #VALOR 2 RESTRICCION, VALOR 1 INPUT
    if operador == ">":
        if valor1 > valor2:
            return True
        else:
            return False
    elif operador == ">=":
        if valor1 >= valor2:
            return True
        else:
            return False
    elif operador == "<=":
        if valor1 <= valor2:
            return True
        else:
            return False
    elif operador == "<":
        if valor1 < valor2:
            return True
        else:
            return False
    elif operador == "=":
        if valor1 == valor2:
            return True
        else:
            return False
    else:
        return False 


def hacer_calculo(formula, diccionario):
    formula_reemplazada = formula
    for i in formula:
        if i in diccionario.keys():
            formula_reemplazada = formula_reemplazada.replace(i, str(diccionario[i]))
    return eval(formula_reemplazada)
        


@login_required(login_url="/login")
def calculos(request):
    return render(request, "calculos/calculos.html")

@login_required(login_url="/login")
def crear_atributo(request):
    if request.method == "POST":
        nuevo_atributo = Atributo(nombre=request.POST["nombre"], 
                                    abreviacion=request.POST["abreviacion"], 
                                    unidad=request.POST["unidad"])
        nuevo_atributo.save()
        return redirect("/calculos")
    else:
        return render(request, "calculos/crear_atributo.html")

@login_required(login_url="/login")
def crear_calculo(request):
    usuario = str(request.user)
    if (
        usuario == "tacorrea@uc.cl"
        or usuario == "pcorrea"
        or usuario == "rcasascordero"
        or usuario == "vvergara"
        or usuario == "tacorrea"
    ):
        return render(request, "calculos/crear_calculos.html")
    else:
        return redirect("/")

@login_required(login_url="/login")
def mostrar_filtro_calculo(request):
    get = request.GET
    nombre = get["nombre"]
    formula = get["formula"]
    entero = get["entero"]
    if entero == "Si":
        entero = True
    else:
        entero = False
    nuevo_calculo = Calculo(nombre=nombre, formula=formula, entero=entero)
    nuevo_calculo.save()
    productos = Filtro_producto.objects.all()
    productos_calculo = nuevo_calculo.producto_calculo.all()
    myFilter = Filtro_productoFilter(get, queryset=productos)
    payload = {
        "Calculo": nuevo_calculo,
        "myFilter": myFilter,
        "productos_calculo": productos_calculo,
    }
    return render(request, "calculos/elegir_productos.html", payload)


@login_required(login_url="/login")
def guardar_datos_filtro(request):
    get = request.GET
    calculo = Calculo.objects.get(nombre=get["nombre"])
    productos_calculo_anterior = calculo.producto_calculo.all()
    for i in get.getlist("productos"):
        booleano_repeticion = True if productos_calculo_anterior.filter(producto_calculo__nombre=i).exists() else False
    for i in get.getlist("productos"):
        if not booleano_repeticion:
            producto = Producto.objects.get(nombre=i)
            calculo.producto_calculo.add(producto)
            calculo.save()
    productos_proyecto = calculo.producto_calculo.all()
    productos = Filtro_producto.objects.all()
    for i in productos_proyecto:
        if productos.filter(nombre_producto=i):
            s = productos.filter(nombre_producto=i)[0]
            s.utilizado = calculo.nombre
            s.save()
    myFilter = Filtro_productoFilter(get, queryset=productos)
    payload = {"Calculo": calculo,
               "myFilter": myFilter,
               "productos_calculo": productos_proyecto}
    return render(request, "calculos/elegir_productos.html", payload)

def lista_productos(request):
    return redirect("/calculos")

@login_required(login_url="/login")
def crear_control_riesgo(request):
    if request.method == "GET":
        calculos = Calculo.objects.all()
        payload = {
            "calculos":calculos
        }
        return render(request, "calculos/crear_control_riesgo.html", payload)
    else:
        nombre = request.POST["nombre"]
        calculos = request.POST.getlist("calculos")
        categoria = request.POST["categoria"]
        nuevo_control_riesgo = ControlRiesgo(nombre=nombre, categoria=categoria)
        nuevo_control_riesgo.save()
        lista_atributos = []
        for i in calculos:
            aux = []
            calculo = Calculo.objects.get(nombre=i)
            nuevo_control_riesgo.calculos.add(calculo)
            a = lista_abreviaciones(calculo.formula)
            aux.append(calculo)
            aux.append(a)
            lista_atributos.append(aux)
        nuevo_control_riesgo.save()
        lista_final_final = []
        for y in lista_atributos:
            lista_obj_atributos = [y[0]]
            aux = []
            for x in y[1]:
                nuevo_atributo = Atributo.objects.get(abreviacion=x)
                aux.append(nuevo_atributo)
            lista_obj_atributos.append(aux)
            lista_final_final.append(lista_obj_atributos)
        payload = {"Control_riesgo": nuevo_control_riesgo,
                    "lista_obj_atributos": lista_final_final}
        return render(request, "calculos/control_riesgo_restricciones.html", payload)



@login_required(login_url="/login")
def guardar_control_riesgo(request):
    nombre_control = request.POST["nombre_control"]
    control_riesgo = ControlRiesgo.objects.get(nombre=nombre_control)
    atributos = request.POST.getlist("nombre_atributo")
    operador = request.POST.getlist("operador")
    cantidad = request.POST.getlist("cantidad")
    for n, x in enumerate(atributos):
        split = x.split("**")
        nombre_restriccion = nombre_control + " - " + split[0] + " - " + split[1]
        atributo = Atributo.objects.get(nombre=split[0])
        calculo = Calculo.objects.get(nombre=split[1])
        nueva_restriccion = Restricciones(nombre=nombre_restriccion, atributo=atributo, operador=operador[n], calculo=calculo, cantidad=cantidad[n])
        nueva_restriccion.save()
        control_riesgo.restricciones.add(nueva_restriccion)
        control_riesgo.save()
    return redirect("/calculos")

def crear_instalacion(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]
        instalacion = Instalaciones(nombre=nombre)
        instalacion.save()
        control_riesgos = request.POST.getlist("control_riesgo")
        for i in control_riesgos:
            nuevo_control_riesgo = ControlRiesgo.objects.get(nombre=i)
            instalacion.control_riesgo.add(nuevo_control_riesgo)
            instalacion.save()
        return redirect("/calculos")
    else:
        control_riesgos = ControlRiesgo.objects.all()
        deteccion = control_riesgos.filter(categoria="Detección")
        extincion = control_riesgos.filter(categoria="Extinción")
        riesgo = control_riesgos.filter(categoria="Riesgo")
        payload = {
            "Deteccion":deteccion,
            "Extinción":extincion,
            "Riesgo":riesgo
        }
        return render(request, "calculos/crear_instalacion.html", payload)

def crear_instalacion_proyecto(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]
        codigo = request.POST["codigo"]
        instalacion = request.POST["instalacion"]
        fecha_actual = datetime.now()
        instalacion_proyecto = Instalaciones.objects.get(nombre=instalacion)
        nueva_instalacion_proyecto = InstalacionProyecto(nombre=nombre, codigo=codigo, fecha_creacion=fecha_actual, instalacion=instalacion_proyecto)
        nueva_instalacion_proyecto.save()
        control_riesgos = instalacion_proyecto.control_riesgo.all()
        lista_atributos = []
        for i in control_riesgos:
            for x in i.calculos.all():
                for n in lista_abreviaciones(x.formula):
                    lista_atributos.append(Atributo.objects.get(abreviacion=n))
        sin_repetir = list(dict.fromkeys(lista_atributos))
        payload = {
            "instalacion":nueva_instalacion_proyecto,
            "lista_atributos":sin_repetir,
        }
        return render(request, "calculos/llenar_atributos.html", payload)
    else:
        instalaciones = Instalaciones.objects.all()
        payload = {
            "instalaciones":instalaciones,
        }
        return render(request, "calculos/crear_instalacion_proyecto.html", payload)

def eleccion_control(request):
    if request.method == "POST":
        instalacion_proyecto = request.POST["instalacion"]
        valores = request.POST.getlist("valores")
        atributos = request.POST.getlist("atributo")
        diccionario_atributos = {}
        for n, i in enumerate(atributos):
            diccionario_atributos[i] = float(valores[n])
        lista_control_riesgos = []
        instalacion = InstalacionProyecto.objects.get(nombre=instalacion_proyecto)
        instancia_instalacion = instalacion.instalacion
        control_riesgos = instancia_instalacion.control_riesgo.all()
        for i in control_riesgos:
            booleano = True
            for x in i.restricciones.all():
                if not operador(diccionario_atributos[x.atributo.nombre],x.operador, x.cantidad):
                    booleano = False
            if booleano:
                lista_control_riesgos.append(i)
        payload = {
            "instalacion":instalacion,
            "lista_control_riesgos":lista_control_riesgos,
            "valores":valores,
            "atributos":atributos,
        }
        return render(request, "calculos/eleccion_control_riesgo.html", payload)

def recibir_controles(request):
    if request.method == "POST":
        instalacion = request.POST["instalacion"]
        atributos = request.POST.getlist("atributos")
        valores = request.POST.getlist("valores")
        diccionario_atributos = {}
        for n, x in enumerate(atributos):
            attr = Atributo.objects.get(nombre=x).abreviacion
            diccionario_atributos[attr] = float(valores[n])
        control_riesgo = request.POST.getlist("control_riesgo")
        instancia_instalacion = InstalacionProyecto.objects.get(nombre=instalacion)
        for i in control_riesgo:
            instancia_control_riesgo = ControlRiesgo.objects.get(nombre=i)
            instancia_instalacion.controles_riesgo.add(instancia_control_riesgo)
            instancia_instalacion.save()
        lista_control_riesgos = []
        for x in instancia_instalacion.controles_riesgo.all():
            primera_lista = [x]
            segunda_lista = []
            for n in x.calculos.all():
                auxiliar = []
                auxiliar_productos = []
                auxiliar.append(n)
                auxiliar.append(hacer_calculo(n.formula, diccionario_atributos))
                for k in n.producto_calculo.all():
                    auxiliar_productos.append(k)
                    auxiliar.append(auxiliar_productos)
                segunda_lista.append(auxiliar)
            primera_lista.append(segunda_lista)
            lista_control_riesgos.append(primera_lista)   
        payload = {
            "instalacion":instancia_instalacion,
            "lista_control_riesgos":lista_control_riesgos
        }
        return render(request, "calculos/eleccion_productos_calculos.html", payload)

def eleccion_productos_calculos(request):
    if request.method == "POST":
        instalacion = request.POST["instalacion"]
        valor_calculo = request.POST.getlist("valor_calculo")
        productos = request.POST.getlist("producto")
        instancia_instalacion = InstalacionProyecto.objects.get(nombre=instalacion)
        for n, i in enumerate(productos):
            instancia_producto = Producto.objects.get(id=i)
            nuevo_producto_proyecto = Producto_proyecto_cantidades(id=uuid.uuid1(), producto=instancia_producto, cantidades=valor_calculo[n])
            nuevo_producto_proyecto.save()
            instancia_instalacion.productos_asociados.add(nuevo_producto_proyecto)
            instancia_instalacion.save()
        return redirect("/calculos")

@login_required(login_url="/login")
def mostrar_atributos(request):
    atributos = Atributo.objects.all()
    payload = {
        "atributos":atributos
    }
    return render(request, "calculos/atributos.html", payload)

@login_required(login_url="/login")
def atributo(request, nombre):
    atributo = Atributo.objects.get(nombre=nombre)
    payload = {
        "atributo":atributo
    }
    return render(request, "calculos/atributo.html", payload)

@login_required(login_url="/login")
def mostrar_edicion_atributo(request, nombre):
    atributo = Atributo.objects.get(nombre=nombre)
    if request.method == "POST":
        nueva_abreviacion = request.POST["abreviacion"]
        nueva_unidad = request.POST["unidad"]
        atributo.abreviacion = nueva_abreviacion
        atributo.unidad = nueva_unidad
        atributo.save()
        return redirect("/mostrar_atributos")
    else:
        payload = {
            "atributo":atributo
        }
        return render(request, "calculos/editar_atributo.html", payload)


@login_required(login_url="/login")
def eliminar_atributo(request, nombre):
    atributo =Atributo.objects.get(nombre=nombre)
    atributo.delete()
    return redirect("/mostrar_atributos")

@login_required(login_url="/login")
def mostrar_calculos(request):
    calculos = Calculo.objects.all()
    payload = {
        "calculos":calculos
    }
    return render(request, "calculos/mostrar_calculos.html", payload)

@login_required(login_url="/login")
def mostrar_calculo(request, nombre):
    calculo = Calculo.objects.get(nombre=nombre)
    productos = calculo.producto_calculo.all()
    payload = {
        "calculo":calculo,
        "productos":productos
    }
    return render(request, "calculos/mostrar_calculo.html", payload)

@login_required(login_url="/login")
def mostrar_edicion_calculo(request, nombre):
    calculo = Calculo.objects.get(nombre=nombre)
    if request.method == "POST":
        formula = request.POST["formula"]
        entero = request.POST["entero"]
        productos = request.POST.getlist("producto")
        if len(productos) != 0:
            for i in productos:
                producto = Producto.objects.get(id=i)
                calculo.producto_calculo.remove(producto)
        calculo.save()
        calculo.formula = formula
        if entero == "si":
            calculo.entero = True
        else:
            calculo.entero = False
        calculo.save()
        return redirect("/mostrar_calculos")
    else:
        productos = calculo.producto_calculo.all()
        payload = {
            "calculo":calculo,
            "productos":productos
        }
        return render(request, "calculos/editar_calculo.html", payload)


@login_required(login_url="/login")
def eliminar_calculo(request, nombre):
    calculo = Calculo.objects.get(nombre=nombre)
    calculo.delete()
    return redirect("/mostrar_calculos")

@login_required(login_url="/login")
def mostrar_restricciones(request):
    restricciones = Restricciones.objects.all()
    payload = {
        "restricciones":restricciones
    }
    return render(request, "calculos/mostrar_restricciones.html", payload)

@login_required(login_url="/login")
def restriccion(request, nombre):
    restriccion = Restricciones.objects.get(nombre=nombre)
    payload = {
        "restriccion":restriccion,
    }
    return render(request, "calculos/restriccion.html", payload)

@login_required(login_url="/login")
def mostrar_edicion_restriccion(request, nombre):
    restriccion = Restricciones.objects.get(nombre=nombre)
    if request.method == "POST":
        cantidad = request.POST["cantidad"]
        operador = request.POST["operador"]
        restriccion.cantidad = float(cantidad)
        restriccion.operador = operador
        restriccion.save()
        return redirect("/mostrar_restricciones")
    else:
        payload = {
            "restriccion":restriccion,
        }
        return render(request, "calculos/editar_restriccion.html", payload)


@login_required(login_url="/login")
def eliminar_restriccion(request, nombre):
    restriccion = Restricciones.objects.get(nombre=nombre)
    restriccion.delete()
    return redirect("/mostrar_restricciones")


@login_required(login_url="/login")
def mostrar_controles_riesgo(request):
    control_riesgo = ControlRiesgo.objects.all()
    payload = {
        "control_riesgo":control_riesgo
    }
    return render(request, "calculos/mostrar_controles_riesgo.html", payload)

@login_required(login_url="/login")
def control_riesgo(request, nombre):
    control_riesgo = ControlRiesgo.objects.get(nombre=nombre)
    calculos = control_riesgo.calculos.all()
    restricciones = control_riesgo.restricciones.all()
    payload = {
        "control_riesgo":control_riesgo,
        "calculos":calculos,
        "restricciones":restricciones
    }
    return render(request, "calculos/control_riesgo.html", payload)

@login_required(login_url="/login")
def editar_control_riesgo(request, nombre):
    control_riesgo = ControlRiesgo.objects.get(nombre=nombre)
    if request.method == "POST":
        categoria = request.POST["categoria"]
        control_riesgo.categoria = categoria
        control_riesgo.save()
        return redirect("/mostrar_controles_riesgo")
    else:
        payload = {
            "control_riesgo":control_riesgo,
        }
        return render(request, "calculos/editar_control_riesgo.html", payload)

@login_required(login_url="/login")
def eliminar_control_riesgo(request, nombre):
    control_riesgo = ControlRiesgo.objects.get(nombre=nombre)
    control_riesgo.delete()
    return redirect("/mostrar_controles_riesgo")