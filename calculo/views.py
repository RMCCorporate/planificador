from django.shortcuts import render
from django.shortcuts import render, redirect
from planificador.models import (
    Atributo,
    Calculo,
    Precio,
    Producto,
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
    return list(dict.fromkeys(lista))


@login_required(login_url="/login")
def calculos(request):
    print(int(2.5)+1)
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
    return render(request, "calculos/elegir_productos", payload)


@allowed_users(allowed_roles=["Admin", "Planificador"])
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
    return render(request, "calculos/elegir_productos", payload)
