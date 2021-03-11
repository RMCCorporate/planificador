from django.shortcuts import render

# Create your views here.
def index(request):
    print("PRUEBA GIt")
    return render(request, 'planificador/index.html')