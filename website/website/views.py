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
from .models import Habit, HabitCompletion, custom_user, Achievement
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now, localtime
from .forms import SkipHabitForm
from django.db.models import F, Window
from django.db.models.functions import Rank
from django.contrib.auth.models import User
from .models import Friend


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
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            unlock_achievement(user, "New Recruit", f"🌍 Joined on {timezone.now().date()}.", request)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    #sorting the Query List in the order of importance
    all_habits = Habit.objects.filter(user=request.user).order_by('-important')

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
    unlock_achievement(request.user, "Self Scan", "👨‍🚀 View your own profile.", request)
    user = request.user
    achievements = Achievement.objects.filter(user=user)
    return render(request, 'my_profile.html', {'achievements': achievements})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST, instance=request.user)
        custom_form = EditCustomUserProfileForm(request.POST, request.FILES, instance=request.user.custom_user)  # Add `request.FILES`
        if form.is_valid() and custom_form.is_valid():
            form.save()
            custom_form.save()
            return redirect('my_profile')
        
        # achievement
        unlock_achievement(request.user, "Bio Uploaded", "📄 Edit your profile for the first time.", request)

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

    # achievements
    completions = HabitCompletion.objects.filter(habit__user=request.user).count()
    if completions >= 1:
        unlock_achievement(request.user, "First Launch", "🚀 Complete your first habit.", request)
    if completions >= 5:
        unlock_achievement(request.user, "Mission Control", "🛰️ Complete 5 habits.", request)
    if completions >= 10:
        unlock_achievement(request.user, "Achieve Orbit", "🌌 Complete 10 habits.", request)
    if completions >= 50:
        unlock_achievement(request.user, "Out of this World", "🌠 Complete 50 habits.", request)

    # Unlock streak achievements
    streak = habit.get_current_streak()
    if streak >= 5:
        unlock_achievement(request.user, "Hot Streak", "🔥 Reach a streak of 5.", request)
    elif streak >= 10:
        unlock_achievement(request.user, "On Fire", "🔥🔥 Reach a streak of 10.", request)
    elif streak >= 50:
        unlock_achievement(request.user, "Master of Momentum", "🔥🔥🔥 Reach a streak of 50.", request)

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
def is_important(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == "POST":
        habit.important = True if not habit.important else False
        habit.save()
    return redirect("my_habits")

@login_required
def add_tag(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == "POST":
        data = request.POST
        habit.label = data.get("label_input")
        habit.save()
    return redirect("my_habits")

@login_required
def my_habits(request):
    # achievements
    habit_count = Habit.objects.filter(user=request.user).count()
    if habit_count >= 1:
        unlock_achievement(request.user, "Habit Creator", "🛠️ Create your first habit.", request)
    if habit_count >= 5:
        unlock_achievement(request.user, "Habit Builder", "🏗️ Create 5 habits.", request)

    frequency_filter = request.GET.get('frequency', 'all')
    status_filter = request.GET.get('status', 'all')
    tag_filter = request.GET.get('tag', 'all')

    # show important first
    habits = Habit.objects.filter(user=request.user).order_by('-important', 'name')

    # frequency
    if frequency_filter != 'all':
        habits = habits.filter(frequency=frequency_filter)

    # completion
    if status_filter != 'all':
        if status_filter == 'completed':
            habits = habits.filter(
                id__in=[
                    habit.id for habit in habits
                    if habit.is_completed_today() or habit.is_completed_this_week() or habit.is_completed_this_month()
                ]
            )
        elif status_filter == 'skipped':
            habits = habits.filter(
                id__in=[
                    habit.id for habit in habits
                    if habit.is_skipped_today() or habit.is_skipped_this_week() or habit.is_skipped_this_month()
                ]
            )
        elif status_filter == 'incompleted':
            habits = habits.filter(
                id__in=[
                    habit.id for habit in habits
                    if not habit.is_completed_today() and not habit.is_skipped_today() and not habit.is_completed_this_week() and not habit.is_skipped_this_week() and not habit.is_completed_this_month() and not habit.is_skipped_this_month()
                ]
            )

    # tag
    if tag_filter != 'all':
        habits = habits.filter(label=tag_filter)
    tags = Habit.objects.filter(user=request.user).values_list('label', flat=True).distinct()

    return render(request, 'my_habits.html', {'habits': habits, 'tags': tags})

@login_required
def my_calendar(request):
    return render(request, 'my_calendar.html')

@login_required
def my_progress(request):
    unlock_achievement(request.user, "Progress Tracker", "📊 View your progress.", request)

    user = request.user
    habits = Habit.objects.filter(user=user)
    total_habits = habits.count()
    completed_habits = habits.filter(completions__isnull=False).distinct().count()
    total_missed_habits = sum(habit.get_missed_occurrences() for habit in habits)

    # stats
    overall_completion_rate = (
        (completed_habits / (completed_habits + total_missed_habits)) * 100 if total_habits > 0 else 0
    )
    longest_streak = max((habit.get_max_streak() for habit in habits), default=0)
    current_streak = max((habit.get_current_streak() for habit in habits), default=0)
    total_days_active = (timezone.now().date() - user.date_joined.date()).days

    return render(request, 'my_progress.html', {
        'daily_percentage': int((completed_habits / total_habits) * 100) if total_habits > 0 else 0,
        'completed_habits': completed_habits,
        'total_habits': total_habits,
        'total_missed_habits': total_missed_habits,
        'overall_completion_rate': round(overall_completion_rate, 2),
        'longest_streak': longest_streak,
        'current_streak': current_streak,
        'total_days_active': total_days_active,
    })

@login_required
def leaderboard(request):

    unlock_achievement(request.user, "Galactic Observer", "🏆 View the leaderboards.", request)

    # sort by total exp
    all_users = custom_user.objects.annotate(
        user_rank=Window(
            expression=Rank(),
            order_by=[F('total_exp').desc()]
        )
    )
    self = all_users.filter(user=request.user).first()
    top100 = all_users.order_by('user_rank')[:100]

    # get times
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    # number of habits completed
    completions_today = HabitCompletion.objects.filter(date_completed=today).select_related('habit', 'habit__user')
    completions_this_week = HabitCompletion.objects.filter(date_completed__gte=start_of_week).select_related('habit', 'habit__user')
    completions_this_month = HabitCompletion.objects.filter(date_completed__gte=start_of_month).select_related('habit', 'habit__user')

    # get top 10 users by habits completed
    def gettemptop10(completions):
        stats = {}

        for completion in completions:
            user = completion.habit.user

            if user not in stats:
                stats[user] = {
                    'username': user.username,
                    'habits_done': 0,
                    'exp_gained': 0,
                }
            stats[user]['habits_done'] += 1
            stats[user]['exp_gained'] += completion.habit.get_experience_value()
        return sorted(stats.values(), key=lambda x: (x['habits_done'], x['exp_gained']), reverse=True)[:10]
    
    
    top_today = gettemptop10(completions_today)
    top_week = gettemptop10(completions_this_week)
    top_month = gettemptop10(completions_this_month)

    context = {
        'self': self,
        'top100': top100,
        'top_today': top_today,
        'top_week': top_week,
        'top_month': top_month,
    }
    return render(request, 'leaderboard.html', context)

@login_required
def get_habits(request):
    user = request.user 
    habits = Habit.objects.filter(user=user)
    habit_list = []

    for habit in habits:
        #getting the completed_dates list
        completed_dates = habit.completions.values_list('date_completed', flat=True)
        #getting the skipped_dates list
        skipped_dates = habit.skips.values_list('date_skipped', flat=True)
        #converting the date into ISO format
        completed_dates_iso = [date.isoformat() for date in completed_dates]
        skipped_dates_iso = [date.isoformat() for date in skipped_dates]

        habit_property = {
            'title': habit.name,
            'allDay': True,
            'completed_dates' : completed_dates_iso,
            'skipped_dates' : skipped_dates_iso,
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
    current_time = localtime().time()
    print(f"Current server time: {current_time}")

    habits = Habit.objects.filter(active=True)

    for habit in habits:
        if habit.reminder_time:
            # 1 min window
            reminder_time_start = (datetime.combine(date.today(), habit.reminder_time) - timedelta(seconds=30)).time()
            reminder_time_end = (datetime.combine(date.today(), habit.reminder_time) + timedelta(seconds=30)).time()

            print(f"{habit.name} for user: {habit.user.username}, time window: {reminder_time_start} - {reminder_time_end}")
            print(f"Reminder time: {habit.reminder_time}, Weekly: {habit.reminder_weekly}, Monthly: {habit.reminder_monthly}")

            if reminder_time_start <= current_time <= reminder_time_end:
                if habit.frequency == 'daily':
                    print(f"Sending daily reminder")
                    send_reminder_email(habit)
                elif habit.frequency == 'weekly' and habit.reminder_weekly == localtime().weekday():
                    print(f"Sending weekly reminder")
                    send_reminder_email(habit)
                elif habit.frequency == 'monthly' and habit.reminder_monthly == localtime().day:
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
    daily_habits_skipped = 0
    weekly_habits_skipped = 0
    monthly_habits_skipped = 0

    statistics = {}
    for habit in habits:
        if habit.frequency == 'daily':
            daily_habit += 1 
            daily_habits_done += 1 if habit.is_completed_today() else 0
            daily_habits_skipped += 1 if habit.is_skipped_today() else 0
        
        elif habit.frequency == 'weekly':
            weekly_habit += 1
            weekly_habits_done += 1 if habit.is_completed_this_week() else 0
            weekly_habits_skipped += 1 if habit.is_skipped_this_week else 0
        else:
            monthly_habit += 1
            monthly_habits_done += 1 if habit.is_completed_this_month() else 0
            monthly_habits_skipped += 1 if habit.is_skipped_this_month() else 0


    daily_habit_stat = {
        'daily_habits_done': daily_habits_done,
        'daily_habits_skipped' : daily_habits_skipped,
        'daily_habits_missed': daily_habit - daily_habits_done - daily_habits_skipped
    }

    weekly_habit_stat = {
        'weekly_habits_done': weekly_habits_done,
        'weekly_habits_skipped' : weekly_habits_skipped,
        'weekly_habits_missed': weekly_habit - weekly_habits_done - weekly_habits_skipped
    }

    monthly_habit_stat = {
        'monthly_habits_done' : monthly_habits_done,
        'monthly_habits_skipped' : monthly_habits_skipped,
        'monthly_habits_missed' : monthly_habit -  monthly_habits_done - monthly_habits_skipped
    }

    statistics = {
        'daily_habit_stat': daily_habit_stat,
        'weekly_habit_stat':weekly_habit_stat,
        'monthly_habit_stat': monthly_habit_stat,
    }

    return JsonResponse(statistics, safe=False)

@login_required
def weekly_stats(request):
    #stats variable
    # initializing to zero in case of no entry
    weekly_stats  = {
        'Monday' : 0,
        'Tuesday' : 0,
        'Wednesday' : 0,
        'Thursday' : 0,
        'Friday' : 0,
        'Saturday' : 0,
        'Sunday' : 0,
    }

    #getting todays date and the start date
    today = timezone.now().date()
    start_date = today - timedelta(6)

    # getting all the habits of the user
    user_habits = Habit.objects.filter(user=request.user)

    # filtering all the dates in the habit_completion
    # model and using the foreign key relation to get
    # a list of habit completed in the last seven days
    habits = HabitCompletion.objects.filter(
        habit__in = user_habits,
        date_completed__gte= start_date, 
        date_completed__lte= today,
    ).select_related('habit')

    for habit in habits:
        day = habit.date_completed.weekday()
        match day:
            case 0:
                weekly_stats["Monday"] += 1
            case 1:
                weekly_stats["Tuesday"] += 1
            case 2:
                weekly_stats["Wednesday"] += 1
            case 3:
                weekly_stats["Thursday"] += 1
            case 4:
                weekly_stats["Friday"] += 1
            case 5:
                weekly_stats["Saturday"] += 1
            case 6:
                weekly_stats["Sunday"] += 1
    
    return JsonResponse(weekly_stats, safe=False)

@login_required
def level_up_notification(request):
    level_up_data = request.session.pop('level_up_data', None)

    if not level_up_data:
        return redirect('dashboard')
    return render(request, 'level_up_notification.html', {'level_up_data': level_up_data})

@login_required
def skip_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)

    if request.method == 'POST':
        form = SkipHabitForm(request.POST)
        if form.is_valid():
            skip = form.save(commit=False)
            skip.habit = habit
            skip.date_skipped = now().date()
            skip.save()
            return redirect('my_habits')
    else:
        form = SkipHabitForm()

    return render(request, 'skip_habit.html', {'form': form, 'habit': habit})

def unlock_achievement(user, name, description, request=None):
    if not Achievement.objects.filter(user=user, name=name).exists():
        Achievement.objects.create(
            user=user,
            name=name,
            description=description,
            date_unlocked=timezone.now()
        )
        if request:
            messages.success(request, f"🎉 Achievement Unlocked: {name} - {description}")

@login_required
def add_friend(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if to_user != request.user:
        #invite
        Friend.objects.get_or_create(from_user=request.user, to_user=to_user, defaults={'status': 'pending'})
    return redirect('friends_list')

@login_required
def accept_friend_request(request, friend_id):
    friend_request = get_object_or_404(Friend, id=friend_id, to_user=request.user, status='pending')
    friend_request.status = 'accepted'
    friend_request.save()
    return redirect('friends_list')

@login_required
def decline_friend_request(request, friend_id):
    friend_request = get_object_or_404(Friend, id=friend_id, to_user=request.user, status='pending')
    friend_request.status = 'declined'
    friend_request.save()
    return redirect('friends_list')


@login_required
def delete_friend(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    Friend.objects.filter(from_user=request.user, to_user=to_user).delete()
    return redirect('friends_list')

@login_required
def friends_list(request):
    query = request.GET.get('q', '')
    
    all_users = []
    if query:
        all_users = User.objects.filter(username=query).exclude(id=request.user.id)
    else:
        all_users = User.objects.exclude(id=request.user.id)

    # accepted friends
    friends = Friend.objects.filter(from_user=request.user, status='accepted').select_related('to_user')
    
    # friends requests
    friend_requests = Friend.objects.filter(to_user=request.user, status='pending').select_related('from_user')

    return render(request, 'friends_list.html', {
        'all_users': all_users,
        'friends': friends,
        'friend_requests': friend_requests,
        'query': query,
    })


@login_required
def user_profile(request, user_id):
    user_profile = get_object_or_404(User, id=user_id)
    return render(request, 'user_profile.html', {'user_profile': user_profile})
