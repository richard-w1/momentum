from datetime import date, timedelta, datetime
import random
from django.contrib import messages
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, UserChangeForm, UserCreationForm
)
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from .forms import (
    CustomUserCreationForm, EditCustomUserProfileForm, EditUserProfileForm, HabitForm
)
from .models import Habit, HabitCompletion, custom_user
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now, localtime
from .models import Habit

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
                auth_login(request, user)
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

    all_habits = Habit.objects.filter(user=request.user)

    daily_habits = [habit for habit in all_habits if habit.frequency == 'daily']
    weekly_habits = [habit for habit in all_habits if habit.frequency == 'weekly']
    monthly_habits = [habit for habit in all_habits if habit.frequency == 'monthly']

    # stats
    today = date.today()
    completed_today = HabitCompletion.objects.filter(
        habit__user=request.user, date_completed=today).count()
    top_streaks = sorted(
        list(all_habits), key=lambda x: x.get_current_streak(), reverse=True)[:3]
    top_max_streaks = sorted(
        list(all_habits), key=lambda x: x.get_max_streak(), reverse=True)[:3]
    top_completion_rates = sorted(
        list(all_habits), key=lambda x: x.get_completion_rate(), reverse=True)[:3]
    missed_habits = [habit for habit in all_habits if habit.get_missed_occurrences() > 0]
    total_completions = HabitCompletion.objects.filter(habit__user=request.user).count()
    
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
    
    # progress card
    habits = Habit.objects.filter(user=request.user)
    total_habits = habits.count()
    completed_habits = habits.filter(completions__isnull=False).distinct().count()  # adjust if needed
    daily_percentage = int((completed_habits / total_habits) * 100) if total_habits > 0 else 0

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
        'daily_percentage': daily_percentage,
        'completed_habits': completed_habits,
        'total_habits': total_habits
    }
    return render(request, 'dashboard.html', context)

@login_required
def my_profile(request):
    return render(request, 'my_profile.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST, instance=request.user)
        custom_form = EditCustomUserProfileForm(request.POST, request.FILES, instance=request.user.custom_user)  # Add `request.FILES`
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
    today = timezone.now().date()

    if habit.frequency == 'daily' and habit.is_completed_today():
        return redirect("my_habits")
    elif habit.frequency == 'weekly' and habit.is_completed_this_week():
        return redirect("my_habits")
    elif habit.frequency == 'monthly' and habit.is_completed_this_month():
        return redirect("my_habits")
    HabitCompletion.objects.create(habit=habit, date_completed=today)

    profile = habit.user.custom_user
    old_level = profile.level
    old_location = profile.get_current_location()

    profile.total_exp += habit.get_experience_value()
    profile.update_progress()

    # check if lvl up
    if profile.level > old_level:
        new_location = profile.get_current_location()
        level_up_data = {
            'new_level': profile.level,
            'new_location': new_location if new_location != old_location else None
        }
        request.session['level_up_data'] = level_up_data
        return redirect('level_up_notification')

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
    return render(request, 'my_habits.html', {'habits': habits})

@login_required
def my_calendar(request):
    return render(request, 'my_calendar.html')

@login_required
def my_progress(request):
    habits = Habit.objects.filter(user=request.user)
    total_habits = habits.count()
    completed_habits = habits.filter(completions__isnull=False).distinct().count()  # adjust if needed
    daily_percentage = int((completed_habits / total_habits) * 100) if total_habits > 0 else 0

    return render(request, 'my_progress.html', {
        'daily_percentage': daily_percentage,
        'completed_habits': completed_habits,
        'total_habits': total_habits
    })

@login_required
def leaderboard(request):
    return render(request, 'leaderboard.html')

@login_required
def get_habits(request):
    user = request.user 
    habits = Habit.objects.filter(user=user)
    habit_list = []

    for habit in habits:
        #getting the completed_dates list
        completed_dates = habit.completions.values_list('date_completed', flat=True)
        #converting the date into ISO format
        completed_dates_iso = [date.isoformat() for date in completed_dates]

        habit_property = {
            'title': habit.name,
            'allDay': True,
            'completed_dates' : completed_dates_iso,
        }
        if(habit.frequency != 'monthly'):
            habit_property['startRecur'] = habit.created_at.isoformat()
            habit_property['daysOfWeek'] = list(range(7)) if habit.frequency == 'daily' else [0]
        else:
            habit_property['rrule'] = {
                'freq': 'monthly',
                'dtstart': habit.created_at.isoformat(),
                'bymonthday': [habit.created_at.day]
            }
        
        habit_list.append(habit_property)
        
    return JsonResponse(habit_list, safe=False)


#momentumhabitapp@gmail.com
#momentum123
@login_required
def send_habit_notifications(request):
    user = request.user
    today = timezone.now().date()

    habits = user.habit_set.filter(active=True)

    daily_incomplete = []
    weekly_incomplete = []
    monthly_incomplete = []

    for habit in habits:
        if habit.frequency == 'daily' and not habit.is_completed_today():
            daily_incomplete.append(habit)
        elif habit.frequency == 'weekly' and not habit.is_completed_this_week():
            weekly_incomplete.append(habit)
        elif habit.frequency == 'monthly' and not habit.is_completed_this_month():
            monthly_incomplete.append(habit)

    context = {
        'user': user,
        'daily_incomplete': daily_incomplete,
        'weekly_incomplete': weekly_incomplete,
        'monthly_incomplete': monthly_incomplete,
        'today': today,
    }

    html_message = render_to_string('habit_notification_email.html', context)
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            'Incomplete Habits Notification',
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
        )
        messages.success(request, 'Notification email sent successfully!')
    except Exception as e:
        messages.error(request, f'Failed to send notification: {str(e)}')

    return redirect('dashboard')

def send_habit_reminders():
    #convert to server timezone
    current_time = localtime().time()
    print(f"Current server time: {current_time}")

    habits = Habit.objects.filter(active=True)

    for habit in habits:
        if habit.reminder_time:
            #1 minute time window
            reminder_time_start = (datetime.combine(date.today(), habit.reminder_time) - timedelta(seconds=30)).time()
            reminder_time_end = (datetime.combine(date.today(), habit.reminder_time) + timedelta(seconds=30)).time()

            print(f"{habit.name} for user: {habit.user.username}, time window: {reminder_time_start} - {reminder_time_end}")

            if reminder_time_start <= current_time <= reminder_time_end:
                if habit.frequency == 'daily':
                    print(f"Sending daily reminder")
                    send_reminder_email(habit)
                elif habit.frequency == 'weekly' and habit.reminder_weekly == now().weekday():
                    print(f"Sending weekly reminder")
                    send_reminder_email(habit)
                elif habit.frequency == 'monthly' and habit.reminder_monthly == now().day:
                    print(f"Sending monthly reminder")
                    send_reminder_email(habit)
            else:
                print(f"Not sending reminder")

def send_reminder_email(habit):
    subject = f"Reminder: {habit.name}"
    message = f"Hi {habit.user.username},\n\nThis is a reminder to complete your habit: {habit.name}."
    recipient_list = [habit.user.email]

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

@login_required
def get_stats(request):
    habits = Habit.objects.filter(user = request.user)

    # general stats variable
    daily_habit = 0
    weekly_habit = 0
    monthly_habit = 0
    daily_habits_done = 0
    weekly_habits_done = 0
    monthly_habits_done = 0

    statistics = {}
    for habit in habits:
        if habit.frequency == 'daily':
            daily_habit += 1 
            daily_habits_done += 1 if habit.is_completed_today() else 0
        
        elif habit.frequency == 'weekly':
            weekly_habit += 1
            weekly_habits_done += 1 if habit.is_completed_this_week() else 0
        else:
            monthly_habit += 1
            monthly_habits_done += 1 if habit.is_completed_this_month() else 0


    daily_habit_stat = {
        'daily_habits_done': daily_habits_done,
        'daily_habits_missed': daily_habit - daily_habits_done
    }

    weekly_habit_stat = {
        'weekly_habits_done': weekly_habits_done,
        'weekly_habits_missed': weekly_habit - weekly_habits_done
    }

    monthly_habit_stat = {
        'monthly_habits_done' : monthly_habits_done,
        'monthly_habits_missed' : monthly_habit -  monthly_habits_done,
    }

    statistics = {
        'daily_habit_stat': daily_habit_stat,
        'weekly_habit_stat':weekly_habit_stat,
        'monthly_habit_stat': monthly_habit_stat,
    }

    return JsonResponse(statistics, safe=False)

@login_required
def level_up_notification(request):
    level_up_data = request.session.pop('level_up_data', None)

    if not level_up_data:
        return redirect('dashboard')
    return render(request, 'level_up_notification.html', {'level_up_data': level_up_data})