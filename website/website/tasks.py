from celery import shared_task
from django.utils.timezone import now
from .models import Habit
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_habit_reminders_task():
    habits = Habit.objects.filter(active=True)

    for habit in habits:
        if habit.reminder_time:
            if habit.frequency == 'daily' and habit.reminder_time == now().time():
                send_reminder_email(habit)
            elif habit.frequency == 'weekly' and habit.reminder_weekly == now().weekday() and habit.reminder_time == now().time():
                send_reminder_email(habit)
            elif habit.frequency == 'monthly' and habit.reminder_monthly == now().day and habit.reminder_time == now().time():
                send_reminder_email(habit)

def send_reminder_email(habit):
    subject = f"Reminder: {habit.name}"
    message = f"Hi {habit.user.username},\n\nThis is a reminder to complete your habit: {habit.name}."
    recipient_list = [habit.user.email]

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)