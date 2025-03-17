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
    
    def get_streak(self):
        completions = self.completions.order_by('-date_completed')
        streak = 0
        if not completions.exists():
            return streak
        
        today = date.today()
        expected_gap = timedelta(
            days=1 if self.frequency == 'daily' 
            else (7 if self.frequency == 'weekly' 
            else 30))
        for i, completion in enumerate(completions):
            if i == 0 and completion.date_completed == today:
                streak += 1
            elif i > 0 and (completions[i-1].date_completed - completion.date_completed) == expected_gap:
                streak += 1
            else:
                break
        
        return streak

    
class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    date_completed = models.DateField()

    def __str__(self):
        return f"{self.habit.name} completed on {self.date_completed}"