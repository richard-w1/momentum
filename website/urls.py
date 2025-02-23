from django.contrib import admin
from django.urls import path, include
from . import views
from website.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('landing/', landing, name = 'landing'),
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('', home_redirect, "Redirection"),
]
