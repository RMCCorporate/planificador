from django.shortcuts import render
from django.shortcuts import render, redirect
from planificador.models import (
    Atributo,
    Calculo,
    ControlRiesgo,
    Instalaciones,
    Precio,
    Producto,
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

@login_required(login_url="/login")
def calculos(request):
    formula = "2*H+H+W*(int(L/S)+1)+D"
    parentesis = formula[formula.find("(")+1:formula.rfind(")")]
    formulas = calculo_parentesis(formula, [])
    lista_string = [formula]
    lista_atributos = lista_abreviaciones(formula)
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
        print(lista_atributos)
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
        print(" ")
        print(lista_final_final)
        for i in lista_final_final:
            print(i)
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
            print(nuevo_control_riesgo)
            instalacion.control_riesgo.add(nuevo_control_riesgo)
            for x in instalacion.control_riesgo.all():
                print(x)
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
                aux = []
                aux.append(x)
                aux_atributos = [] 
                for n in lista_abreviaciones(x.formula):
                    aux_atributos.append(Atributo.objects.get(abreviacion=n))
                aux.append(aux_atributos)
                aux.append(i)
                lista_atributos.append(aux)
        payload = {
            "instalacion":nueva_instalacion_proyecto,
            "lista_atributos":lista_atributos
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
        instalacion = request.POST["instalacion"]
        valores = request.POST.getlist("valores")
        atributos = request.POST.getlist("atributo")
        calculos = request.POST.getlist("calculo")
        controlriesgo = request.POST.getlist("controlriesgo")
        controlriesgo_sin_repetir = list(dict.fromkeys(controlriesgo))
        diccionario_restricciones = {}
        for x in controlriesgo_sin_repetir:
            diccionario_restricciones[x] = []
        for n, i in enumerate(valores):
            atributo = Atributo.objects.get(nombre=atributos[n])
            calculo = Calculo.objects.get(nombre=calculos[n])
            restriccion = Restricciones.objects.get(atributo=atributo, calculo=calculo)
            control_riesgo = controlriesgo[n]
            diccionario_restricciones[control_riesgo].append([operador(restriccion.cantidad, restriccion.operador, int(i)), atributo, int(i), calculo[n]])
        lista_final = []
        for i in diccionario_restricciones.keys():
            if False not in diccionario_restricciones[i][0]:
                lista_final.append([i, diccionario_restricciones[i]])
        print(diccionario_restricciones)
        print(lista_final)
        payload = {
            "instalacion":instalacion,
            "lista_final":lista_final
        }
        return render(request, "calculos/eleccion_control_riesgo.html", payload)