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

