from django.shortcuts import render
from .models import Visualizacion
from django.http import HttpRequest
from .forms import QueryForm

from datetime import datetime
from persistencia.visualizacion_dbops import get_reports, get_departamentos
from exterior_data.covid_data import chart_edad
# Create your views here.

def visualizacion(request:HttpRequest):
    disease, municipio, barrio = "disease", "municipio", "barrio"
    visualizacions = Visualizacion.objects.all().order_by('-date')
    if request.method == "GET":
        form = QueryForm()
        reports = tuple(get_reports())
        #print(form)
        departamentos = get_departamentos()
        print(departamentos)
        
        context = {"query_form": form,
                "visualizacions":visualizacions,
                "reports": reports,
                }
        return render(request, 'visualizacion.html', context)
        #return render(req, "reporte.html", context)
    elif request.method == "POST":
        form = QueryForm(request.POST)
        if form.is_valid():
            form_data: dict = form.cleaned_data
            form_data['diagnosis_date'] = datetime.combine(form_data['diagnosis_date'], datetime.min.time())
            print(form_data)
            match_stage = {}
            if form_data.get(disease) not in ["Enfermedades", "Enfermedad"]:
                match_stage[disease] = form_data.get(disease)
                #return render(request, "user_error.html")
            if form_data.get(municipio) != "Municipios":
                match_stage[municipio] = form_data.get(municipio)
                #return render(request, "user_error.html")
            if form_data.get(barrio) != "Barrios":
                match_stage[barrio] = form_data.get(barrio)
                #return render(request, "user_error.html")
            
            reports = tuple(get_reports(match_stage))
            """try:
                pass
            except:
                pass"""
            
            
            context = {"query_form": form,
                    "visualizacions":visualizacions,
                    "reports": reports,
                    }
            return render(request, 'visualizacion.html', context)
    
from django.http import JsonResponse
from persistencia.mongo_data import get_db

def get_departamento_ciudad_barrio(request):
    departamento = request.GET.get('departamento')
    ciudad = request.GET.get('ciudad')
    barrio = request.GET.get('barrio')

    collection = get_db()["places"]

    if departamento:
        ciudades = collection.find({'departamento': departamento}, {'municipio': 1})
        ciudades = [ciudad['ciudad'] for ciudad in ciudades]
    else:
        ciudades = []

    if ciudad:
        barrios = collection.find({'municipio': ciudad}, {'centro_poblado': 1})
        barrios = [barrio['barrio'] for barrio in barrios]
    else:
        barrios = []

    response = {
        'departamento': departamento,
        'ciudades': ciudades,
        'barrios': barrios
    }
    print(response)
    return JsonResponse(response)

def bienvenida_visualizaciones(req: HttpRequest):
    context = {}
    return render(req, "bienvenida_visualizaciones.html", context)

def visualiza_covid(req: HttpRequest):
    plot_divs = [chart_edad()]

    context = {"plotdivs": plot_divs}

    return render(req, "visualiza_covid.html", context)