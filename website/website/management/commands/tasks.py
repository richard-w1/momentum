# how to add cron job on linux:
# crontab -e
# * * * * * /home/user/habit-tracker/venv/bin/python /home/user/habit-tracker/manage.py send_reminders >> /home/user/habit-tracker/cron.log 2>&1

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from website.models import Habit
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        habits = Habit.objects.filter(active=True)

        for habit in habits:
            if habit.reminder_time:
                if habit.frequency == 'daily' and habit.reminder_time == now().time():
                    self.send_reminder_email(habit)
                elif habit.frequency == 'weekly' and habit.reminder_weekly == now().weekday() and habit.reminder_time == now().time():
                    self.send_reminder_email(habit)
                elif habit.frequency == 'monthly' and habit.reminder_monthly == now().day and habit.reminder_time == now().time():
                    self.send_reminder_email(habit)

    def send_reminder_email(self, habit):
        subject = f"Reminder: {habit.name}"
        message = f"Hi {habit.user.username},\n\nThis is a reminder to complete your habit: {habit.name}."
        recipient_list = [habit.user.email]

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        self.stdout.write(self.style.SUCCESS(f"Reminder sent for habit: {habit.name}"))