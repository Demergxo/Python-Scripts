from django.shortcuts import render

def dashboard(request):
    return render(request, 'dashboard.html')

def produccion(request):
    return render(request, 'produccion.html')

def inbound(request):
    return render(request, 'inbound.html')

def outbound(request):
    return render(request, 'outbound.html')