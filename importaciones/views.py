from django.shortcuts import render, redirect
from django.http import HttpResponse
from planificador.models import Importaciones, DHL, Destination_charges, Airfreight_charges, Origin_charges
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from planificador.filters import ProveedoresFilter, Filtro_producto
from planificador.decorators import allowed_users
import openpyxl
import uuid

#Mostrar importaciones
@login_required(login_url='/login')
def importaciones(request):
    importaciones = Importaciones.objects.all()
    lenght = len(importaciones)
    return render(request, 'importaciones/importaciones.html', {"importaciones":importaciones, "len":lenght})


def nueva_importacion_planilla(request):
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb["Air Rates Vertical Format"]
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            region = row_data[1]
            if region != "None" and region != "Origin" and region != "Region\n(enter AP, AM, EURO, MEA)":
                #FALTA VER LOS CASOS QUE NO SON INT O ESTÁN VACÍOS!!
                country = row_data[2]
                origin = row_data[4]
                origin_currency = row_data[13]
                pickup_min = row_data[14]
                pickup_kg = row_data[15]
                handling = row_data[16]
                customs_clearence = row_data[17]
                other_fees1_description = row_data[18]
                other_fees1_value_min = row_data[19]
                #VER SI EXISTE OTHER FEES VALUE KG EN EL FINAL
                #other_fees1_value_kg = row_data[15] 
                other_fees2_description = row_data[20]
                other_fees2_value_min = row_data[21]
                other_fees2_value_kg = row_data[22]
                origin_transit_time = row_data[23]
                origin_charges = Origin_charges(origin_airport=origin, currency=origin_currency, pickup_min=pickup_min, pickup_kg=pickup_kg, handling=handling, customs_clearence=customs_clearence, other_fees1_description=other_fees1_description, other_fees1_value_min=other_fees1_value_min, other_fees2_description=other_fees2_description, other_fees2_value_min=other_fees2_value_min, other_fees2_value_kg=other_fees2_value_kg, origin_transit_time=origin_transit_time)
                origin_charges.save()
                freight_currency = row_data[24]
                freight_min = row_data[25]
                freight_less_45 = row_data[26]
                freight_45_100 = row_data[27]
                freight_100_300 = row_data[28]
                freight_300_500 = row_data[29]
                freight_500_1000 = row_data[30]
                freight_more_1000 = row_data[31]
                fuel_surcharge_min = row_data[32]
                fuel_surcharge_kg = row_data[33]
                security_surcharge_min = row_data[34]
                security_surcharge_kg = row_data[35]
                cargo_screening_fee_min = row_data[36]
                cargo_screening_fee_kg = row_data[37]
                airfreight_charges = Airfreight_charges(origin_airport=origin, currency=freight_currency, freight_min=freight_min, freight_less_45=freight_less_45, freight_45_100=freight_45_100, freight_100_300=freight_100_300, freight_300_500=freight_300_500, freight_500_1000=freight_500_1000, freight_more_1000=freight_more_1000, fuel_surcharge_min=fuel_surcharge_min, fuel_surcharge_kg=fuel_surcharge_kg, security_surcharge_min=security_surcharge_min, security_surcharge_kg=security_surcharge_kg, cargo_screening_fee_min=cargo_screening_fee_min, cargo_screening_fee_kg=cargo_screening_fee_kg)
                airfreight_charges.save()
                airline = row_data[38]
                direct_flight = row_data[39]
                departure_days = row_data[40]
                transit_time = row_data[41]
                destination_currency = row_data[42]
                terminal_handling = row_data[43]
                doc_fee_min = row_data[44]
                doc_fee_max = row_data[45]
                doc_fee_kg = row_data[46]
                desconsolidation = row_data[47]
                destination_charges = Destination_charges(origin_airport=origin, currency=destination_currency, terminal_handling=terminal_handling, doc_fee_min=doc_fee_min, doc_fee_max=doc_fee_max, doc_fee_kg=doc_fee_kg, desconsolidation=desconsolidation)
                destination_charges.save()
                dhl = DHL(origin_airport=origin, region=region, country=country, airline=airline, direct_flight=direct_flight, departure_days=departure_days, transit_time=transit_time)
                dhl.save()
                dhl.origin = origin_charges
                dhl.freight = airfreight_charges
                dhl.destination = destination_charges
                dhl.save()
        return redirect('/importaciones')
    else:
        return render(request, 'importaciones/nueva_importacion_planilla.html')