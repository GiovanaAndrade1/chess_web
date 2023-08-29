
from django.shortcuts import render


def dashboard(request):
    return render(request, 'pages/dashboard.html', {
        
    })
def perfil(request):
    return render(request,'pages/perfil.html', {
        
    })