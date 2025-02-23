from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
]