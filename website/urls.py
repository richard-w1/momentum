from django.contrib import admin
from django.urls import path, include
from . import views
from website.views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, "Redirection"),
    path("", include("website.urls")),
]