from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import login as auth_login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, EditUserProfileForm, EditCustomUserProfileForm
from .forms import HabitForm
from .models import Habit, HabitCompletion
from datetime import date
from django.utils import timezone
from datetime import timedelta
import random

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
    if not request.user.is_authenticated:
        return redirect('login')
    
    all_habits = Habit.objects.filter(user=request.user, active=True)

    daily_habits = all_habits.filter(frequency='daily')
    weekly_habits = all_habits.filter(frequency='weekly')
    monthly_habits = all_habits.filter(frequency='monthly')

    # stats
    today = date.today()
    completed_today = HabitCompletion.objects.filter(
        habit__user=request.user, date_completed=today).count()
    

    top_streaks = sorted(list(all_habits), key=lambda x: x.get_streak(), reverse=True)[:3]
    top_completion_rates = sorted(list(all_habits), key=lambda x: x.get_completion_rate(), reverse=True)[:3]

    missed_habits = [habit for habit in all_habits if habit.get_missed_occurrences() > 0]

    total_completions = HabitCompletion.objects.filter(
        habit__user=request.user
    ).count()
    
    tips = [
        "\"The secret of getting ahead is getting started.\" - Mark Twain",
        "\"We become what we repeatedly do.\" - Sean Covey",
        "\"Your beliefs become your thoughts, your thoughts become your words, your words become your actions, your actions become your habits, your habits become your values, your values become your destiny.\" - Gandhi",
        "\"If your habits don't line up with your dream, you either need to change your habits or change your dream.\" - John Maxwell",
        "\"First forget inspiration. Habit is more dependable. Habit will sustain you whether you're inspired or not.\" - Octavia Butler",
        "\"Seek clarity. Generate energy. Raise necessity. Increase productivity. Develop influence. Demonstrate courage.\" - Brendan Burchard",
        "\"If you believe you can change – if you make it a habit – the change becomes real.\" - Charles Duhigg",
        "\"Dreams are lovely. But they are just dreams. It's hard work that makes things happen. It's hard work that creates change.\" - Shonda Rhimes",
        "\"True life is lived when tiny changes occur.\" - Leo Tolstoy",
        "\"Successful people are simply those with successful habits.\" - Brian Tracy",
        "\"Do small things with great love.\" - Mother Teresa",
        "\"It is easier to prevent bad habits than to break them.\" - Benjamin Franklin",
        "\"Our character is basically a composite of our habits. Because they are consistent patterns, they constantly express our character.\" - Stephen Covey",
        "\"If you are going to achieve excellence in big things, you develop the habit in little matters.\" - Colin Powell",
        "\"If you pick the right small behavior and sequence it right, then you won't have to motivate yourself to have it grow. It will just happen naturally.\" - BJ Fogg",
        "\"Excellence is an art won by training and habituation.\" - Aristotle",
        "\"You'll never change your life until you change something you do daily. The secret of your success is found in your daily routine.\" - John C. Maxwell",
        "\"When nothing seems to help, I go and look at a stonecutter hammering away at his rock. Yet at the hundred and first blow it will split in two, and I know it was not that last blow that did it—but all that had gone before.\" - James Clear",
        "\"Energy is usually at its peak during the first part of your day, which means you should be completing habits that inspire or excite you about the day ahead.\" - S.J. Scott",
        "\"If you start with a big behavior that's hard to do, the design is unstable. However, a habit that is easy to do can weather a storm like flexible sprouts.\" - BJ Fogg"
    ]
    random_tip = random.choice(tips)
    
    context = {
        'habit_count': all_habits.count(),
        'daily_habits': daily_habits,
        'weekly_habits': weekly_habits,
        'monthly_habits': monthly_habits,
        'completed_today': completed_today,
        'total_completions': total_completions,
        'top_streaks': top_streaks,
        'top_completion_rates': top_completion_rates,
        'missed_habits': missed_habits,
        'random_tip': random_tip,
    }

    return render(request, 'dashboard.html', context)

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
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('my_profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})

@login_required
def add_habit(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('my_habits')
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
def complete_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if HabitCompletion.objects.filter(habit=habit, date_completed=date.today()).exists():
        return redirect("my_habits")
    HabitCompletion.objects.create(habit=habit, date_completed=date.today())
    habit.last_completed = date.today()
    habit.save()

    return redirect("my_habits")

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
    today = timezone.now().date()
    for habit in habits:
        if habit.frequency == 'daily':
            habit.is_completed_today = HabitCompletion.objects.filter(habit=habit, date_completed=today).exists()
        elif habit.frequency == 'weekly':
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            habit.is_completed_this_week = HabitCompletion.objects.filter(habit=habit, date_completed__range=[start_of_week, end_of_week]).exists()
        elif habit.frequency == 'monthly':
            start_of_month = today.replace(day=1)
            next_month = today.replace(day=28) + timedelta(days=4)
            start_of_next_month = next_month.replace(day=1)
            habit.is_completed_this_month = HabitCompletion.objects.filter(habit=habit, date_completed__range=[start_of_month, start_of_next_month - timedelta(days=1)]).exists()

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