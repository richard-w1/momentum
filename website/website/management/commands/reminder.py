# filepath: website/management/commands/send_reminders.py
from django.core.management.base import BaseCommand
from website.views import send_habit_reminders

class Command(BaseCommand):
    help = 'Send habit reminders'

    def handle(self, *args, **kwargs):
        send_habit_reminders()