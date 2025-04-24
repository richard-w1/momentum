"""
URL configuration for website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import change_password
from .views import send_habit_notifications
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home_redirect),
    path('admin/', admin.site.urls),
    path('api/', include('authentication.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('landing/', views.landing, name='landing'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    path('add_habit/', views.add_habit, name='add_habit'),
    path('my_habits/', views.my_habits, name='my_habits'),
    path("my_habits/add/", views.add_habit, name="add_habit"),
    path("my_habits/<int:habit_id>/edit/", views.edit_habit, name="edit_habit"),
    path("my_habits/<int:habit_id>/delete/", views.delete_habit, name="delete_habit"),
    path("my_habits/<int:habit_id>/complete/", views.complete_habit, name="complete_habit"),
    path("my_habits/<int:habit_id>/important/", views.is_important, name="important_habit"),
    path('my_profile/', views.my_profile, name='my_profile'),
    path('my_profile/edit', views.edit_profile, name='edit_profile'),
    path('change-password/', change_password, name='change_password'),
    path('my_calendar/', views.my_calendar, name='my_calendar'),
    path('get_habits/', views.get_habits, name='get_habits'),
    path('get_stats/', views.get_stats, name='get_stats'),
    path('get_weekly_stats/', views.weekly_stats, name='get_weekly_stats'),
    path('my_progress/', views.my_progress, name='my_progress'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('send-habit-notifications/', send_habit_notifications, name='send_habit_notifications'),
    path('level-up-notification/', views.level_up_notification, name='level_up_notification'),
    path('my_habits/<int:habit_id>/skip/', views.skip_habit, name='skip_habit'),
]

# profile pictures
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

 