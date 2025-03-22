from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta


#creating a custom model for users
class custom_user(models.Model):
    #using the default  model as the basis
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True)
    bio = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.username} custom_user'

class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    last_completed = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.frequency})"
    
    def get_interval(self):
        if self.frequency == 'daily':
            return timedelta(days=1)
        elif self.frequency == 'weekly':
            return timedelta(days=7)
        else:
            return timedelta(days=30)
        
    def get_frequency_display(self):
        for choice in self.FREQUENCY_CHOICES:
            if choice[0] == self.frequency:
                return choice[1]
        return self.frequency
    
    def get_streak(self):
        completions = list(self.completions.order_by('-date_completed').values_list('date_completed', flat=True))
        if not completions:
            return 0
        
        today = date.today()

        if self.frequency == 'daily' and completions[0] != today:
            return 0

        streak = 1
        if len(completions) == 1:
            return streak

        for i in range(len(completions) - 1):
            if completions[i] - completions[i+1] == self.get_interval():
                streak += 1
            else:
                break
        
        return streak

    def get_missed_occurrences(self):
        if not self.last_completed:
            return 0
        
        today = date.today()
        
        expected_dates = []
        current_date = self.last_completed + self.get_interval()
        while current_date <= today:
            expected_dates.append(current_date)
            current_date += self.get_interval()
        
        if not expected_dates:
            return 0
        
        completed_dates = set(self.completions.values_list('date_completed', flat=True))
        return sum(1 for date in expected_dates if date not in completed_dates)
    
    def get_completion_rate(self):
        start_date = self.created_at.date()
        today = date.today()
        days_since_creation = (today - start_date).days
        
        if days_since_creation == 0:
            return 100.0
        
        if self.frequency == 'daily':
            total_expected = days_since_creation
        elif self.frequency == 'weekly':
            total_expected = days_since_creation // 7
        else:
            total_expected = days_since_creation // 30
        
        total_expected = max(total_expected, 1)
        total_completions = self.completions.count()
        
        return round((total_completions / total_expected) * 100, 2)

    def is_completed_today(self):
        return self.completions.filter(date_completed=date.today()).exists()

    def is_completed_this_week(self):
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        return self.completions.filter(date_completed__gte=start_of_week).exists()

    def is_completed_this_month(self):
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        return self.completions.filter(date_completed__gte=start_of_month).exists()

class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="completions")
    date_completed = models.DateField(default=date.today)

    class Meta:
        unique_together = ('habit', 'date_completed')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.habit.last_completed = self.date_completed
        self.habit.save()

    def __str__(self):
        return f"{self.habit.name} completed on {self.date_completed}"