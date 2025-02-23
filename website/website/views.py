from django.http import HttpResponse
from django.shortcuts import render

def landing(request):
    return render(request, 'landing.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def dashboard(request):
    return render(request, 'dashboard.html')