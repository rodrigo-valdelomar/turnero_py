from __future__ import print_function

from django.shortcuts import render

from datetime import datetime, timedelta
import os.path

import json

from django.http import HttpResponse

from calen.functions import availableDate, availableAppointment, createAppointment

# from google.auth.transport.requests import Request

def main(request):
    
    if request.method == "POST":
        data = request.body

        dict_str = data.decode("UTF-8")
        my_data = json.loads(dict_str)
        try:
            date = my_data["chat_log"][10]["text"]
        except:
            date = availableDate(request)
            mensaje = {
                "response": {
                "text": ['Seleccione un día:'],
                "response_type": 'LIST',
                "response_options": date,
                "stopChat": "true",
                # "go_to_name": "sarasa"
                }
            }
            json_date = json.dumps(mensaje, indent = 4)
            return HttpResponse(json_date)
            
        try:
            appointment = my_data["chat_log"][12]["text"]
        except:
            aux = date.split("/")
            min = "2022-"+aux[1]+"-"+aux[0]+"T00:00:00-03:00"
            max = "2022-"+aux[1]+"-"+aux[0]+"T23:59:59-03:00"
            appointment = availableAppointment(request, min, max)
            mensaje = {
                "response": {
                "text": ['Seleccione un turno:'],
                "response_type": 'LIST',
                "response_options": appointment,
                "stopChat": "true",
                # "go_to_name": "sarasa"
                }
            }

            json_ap = json.dumps(mensaje, indent = 4)
            return HttpResponse(json_ap)

        try:
            confirmation = my_data["chat_log"][14]["text"]
        except:
            mensaje = {
                "response": {
                "text": ['Desea confirmar el turno?'],
                "response_type": 'LIST',
                "response_options": ["Si", "No"],
                "stopChat": "true",
                # "go_to_name": "sarasa"
                }
            }
            json_conf = json.dumps(mensaje, indent = 4)
            return HttpResponse(json_conf)

        try:
            if my_data["chat_log"][14]["text"] == "Si":
                aux2 = appointment.split(":")
                mail = my_data["collected_data"]["email"]["value"]
                name = my_data["collected_data"]["name"]["value"].capitalize()
                aux = date.split("/")
                fin = aux2[0]+":30"
                start = "2022-"+aux[1]+"-"+aux[0]+"T"+appointment+":00-03:00"
                end = "2022-"+aux[1]+"-"+aux[0]+"T"+fin+":00-03:00"
                tratamiento = my_data["collected_data"]["custom"]["tratamiento"]
                createAppointment(request, name, mail, start, end, tratamiento)
                
                confirmation_text = name+" se reservó el turno para el: "+date+" de "+appointment+" a "+fin+". Te esperamos para tu "+tratamiento.lower()
                print(confirmation_text)
                mensaje = {
                    "response": {
                    "text": [confirmation_text],
                    "response_type": 'TEXT',
                    "response_options": [],
                    "stopChat": "true",
                    "go_to_name": "sarasa"
                    }
                }

                json_fin = json.dumps(mensaje, indent = 4)
                return HttpResponse(json_fin)
        except:
            pass


    return HttpResponse("hizo la consulta")