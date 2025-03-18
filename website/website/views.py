from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, EditUserProfileForm, EditCustomUserProfileForm
from .forms import HabitForm
from .models import Habit, HabitCompletion
from datetime import date


def home_redirect(request):
    return redirect('landing')

def landing(request):
    return render(request, 'landing.html')

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                form.add_error(None, 'Invalid username or password')
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def my_profile(request):
    return render(request, 'my_profile.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST, instance=request.user)
        custom_form= EditCustomUserProfileForm(request.POST, instance=request.user.custom_user)
        if form.is_valid() and custom_form.is_valid():
            form.save()
            custom_form.save()
            return redirect('my_profile')
    else:
        form = EditUserProfileForm(instance=request.user)
        custom_form = EditCustomUserProfileForm(instance=request.user.custom_user)
    return render(request, 'edit_profile.html', {'form': form, 'custom_form': custom_form})

@login_required
def add_habit(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('dashboard')
    else:
        form = HabitForm()

    return render(request, 'add_habit.html', {'form': form})

@login_required
def edit_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == "POST":
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            return redirect("my_habits")
    else:
        form = HabitForm(instance=habit)

    return render(request, "edit_habit.html", {"form": form, "habit": habit})

@login_required
def delete_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == "POST":
        habit.delete()
        return redirect("my_habits")
    return render(request, "delete_habit.html", {"habit": habit})

@login_required
def my_habits(request):
    habits = Habit.objects.filter(user=request.user)
    return render(request, 'my_habits.html', {'habits': habits})

@login_required
def my_calendar(request):
    return render(request, 'my_calendar.html')

@login_required
def my_progress(request):
    return render(request, 'my_progress.html')

@login_required
def leaderboard(request):
    return render(request, 'leaderboard.html')