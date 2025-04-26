from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone
from datetime import date, timedelta, time

#creating a custom model for users
class custom_user(models.Model):
    #level required, rank, location, exp required for each level up
    rank_milestones = [
        (1, "Earthling", "Earth", 1000),
        (5, "Skyward Wanderer", "Atmosphere", 2000),
        (10, "Lunar Explorer", "Moon", 3000),
        (15, "Martian Scout", "Mars", 4000),
        (20, "Storm Rider", "Jupiter", 5000),
        (25, "Ring Voyager", "Saturn", 6000),
        (30, "Ice Drifter", "Uranus", 7000),
        (35, "Deep Diver", "Neptune", 8000),
        (40, "Galactic Traveler", "Milky Way", 9000),
        (45, "Singularity Seeker", "Black Hole", 10000),
        (50, "Starborn Survivor", "Nebula", 11000),
        (55, "Intergalactic Navigator", "Deep Space...", 12000),
    ]

    RANK_CHOICES = [(milestone[1], milestone[1]) for milestone in rank_milestones]

    #using the default  model as the basis
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True)
    bio = models.CharField(max_length=100, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    
    #leveling
    total_exp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    rank = models.CharField(max_length=100, choices=RANK_CHOICES, default="Earthling")

    def __str__(self):
        return f'{self.user.username} custom_user'

    #gets 4th field in rank_milestones
    def get_exp_per_level(self):
        for milestone_level, _, _, exp_per_level in reversed(self.rank_milestones):
            if self.level >= milestone_level:
                return exp_per_level
        return 1000
    
    def get_current_rank(self):
        for milestone_level, rank_title, _, _ in reversed(self.rank_milestones):
            if self.level >= milestone_level:
                return rank_title
        return "Earthling"
    
    def get_current_location(self):
        for milestone_level, _, location, _ in reversed(self.rank_milestones):
            if self.level >= milestone_level:
                return location
        return "Earth"
    
    def set_custom_rank(self, new_rank):
            # Get all available ranks based on user's level
            available_ranks = []
            for milestone_level, rank_title, _, _ in self.rank_milestones:
                if self.level >= milestone_level:
                    available_ranks.append(rank_title)
            
            if new_rank in available_ranks:
                self.rank = new_rank
                self.save()
                return f"Rank set to {new_rank}."
            return "You cannot set this rank yet!"

    #find exp earned from current level onwards
    #so if the user just leveled up, it would be 0 or a low number
    #this is just used to display to the user their progress to the next level
    def get_current_level_exp_total(self):
        total_for_previous_levels = 0
        for level in range(1, self.level):
            for milestone_level, _, _, exp_per_level in reversed(self.rank_milestones):
                if level >= milestone_level:
                    total_for_previous_levels += exp_per_level
                    break
        
        return self.total_exp - total_for_previous_levels

    #update level and rank based on exp
    def update_progress(self):
        accumulated_exp = 0
        new_level = 1

        while True:
            exp_per_level = 1000
            for milestone_level, _, _, exp_amount in reversed(self.rank_milestones):
                if new_level >= milestone_level:
                    exp_per_level = exp_amount
                    break
            if accumulated_exp + exp_per_level > self.total_exp:
                break
            accumulated_exp += exp_per_level
            new_level += 1

        self.level = new_level
        # self.rank = self.get_current_rank()
        self.save()
        
class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    EXPERIENCE_CHOICES = [
        (100, '100 XP'),
        (200, '200 XP'),
        (500, '500 XP'),
        (1000, '1000 XP'),
        (-1, 'Custom XP'),
    ]

    weekly_choices = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    monthly_choices = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
        (11, '11'),
        (12, '12'),
        (13, '13'),
        (14, '14'),
        (15, '15'),
        (16, '16'),
        (17, '17'),
        (18, '18'),
        (19, '19'),
        (20, '20'),
        (21, '21'),
        (22, '22'),
        (23, '23'),
        (24, '24'),
        (25, '25'),
        (26, '26'),
        (27, '27'),
        (28, '28'),
        (29, '29'),
        (30, '30'),
        (31, '31'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    last_completed = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    experience = models.IntegerField(choices=EXPERIENCE_CHOICES)
    custom_experience = models.PositiveIntegerField(null=True, blank=True)
    important = models.BooleanField(default=False)
    label = models.CharField(max_length=100, default="")

    reminder_time = models.TimeField(null=True, blank=True)
    reminder_weekly = models.IntegerField(null=True, blank=True, choices=weekly_choices)
    reminder_monthly = models.IntegerField(null=True, blank=True, choices=monthly_choices)

    def __str__(self):
        return f"{self.name} ({self.frequency})"
    
    def get_interval(self):
        if self.frequency == 'daily':
            return timedelta(days=1)
        elif self.frequency == 'weekly':
            return timedelta(days=7)
        elif self.frequency == 'monthly':
            return timedelta(days=30)
        
    def get_frequency_display(self):
        for choice in self.FREQUENCY_CHOICES:
            if choice[0] == self.frequency:
                return choice[1]
        return self.frequency
    
    def get_current_streak(self):
        completions = list(self.completions.order_by('-date_completed').values_list('date_completed', flat=True))
        if not completions:
            return 0
        
        current_streak = 1
        today = date.today()
        
        if completions[0] == today:
            for i in range(1, len(completions)):
                if completions[i-1] - completions[i] == self.get_interval():
                    current_streak += 1
                else:
                    break
        
        return current_streak
    
    def get_max_streak(self):
        completions = list(self.completions.order_by('-date_completed').values_list('date_completed', flat=True))
        
        if not completions:
            return 0
        
        current_streak = 1
        max_streak = 1
        
        for i in range(1, len(completions)):
            if completions[i-1] - completions[i] == self.get_interval():
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        return max_streak

    def get_missed_occurrences(self):
        if not self.completions.exists():
            return 0
        
        today = date.today()
        first_completion = self.completions.order_by('date_completed').first().date_completed

        current_date = self.created_at.date()
        missed_count = 0
        
        while current_date <= today:
            expected_next_date = current_date + self.get_interval()
            
            if current_date != first_completion and not self.completions.filter(date_completed=current_date).exists():
                missed_count += 1
            
            current_date = expected_next_date
        
        return missed_count
    

    def get_completion_rate(self):
        today = date.today()
        start_date = self.created_at.date()
        
        if self.frequency == 'daily':
            total_expected = max(1, (today - start_date).days + 1)
        elif self.frequency == 'weekly':
            total_expected = max(1, ((today - start_date).days // 7) + 1)
        elif self.frequency == 'monthly':
            total_expected = max(1, ((today - start_date).days // 30) + 1)
        
        total_completions = self.completions.count()
        completion_rate = (total_completions / total_expected) * 100
        return round(min(completion_rate, 100.0), 2)

    def is_completed_today(self):
        today = timezone.now().date()
        return self.completions.filter(date_completed=today).exists()

    def is_completed_this_week(self):
        if self.frequency != 'weekly':
            return False
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return self.completions.filter(
            date_completed__gte=start_of_week, 
            date_completed__lte=end_of_week
        ).exists()

    def is_completed_this_month(self):
        if self.frequency != 'monthly':
            return False
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return self.completions.filter(
            date_completed__gte=start_of_month, 
            date_completed__lte=end_of_month
        ).exists()
    
    def get_experience_value(self):
        return self.custom_experience if self.experience == -1 and self.custom_experience else self.experience
    
    def is_skipped_today(self):
        today = timezone.now().date()
        return self.skips.filter(date_skipped=today).exists()

    def is_skipped_this_week(self):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return self.skips.filter(
            date_skipped__gte=start_of_week,
            date_skipped__lte=end_of_week
        ).exists()

    def is_skipped_this_month(self):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        end_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return self.skips.filter(
            date_skipped__gte=start_of_month,
            date_skipped__lte=end_of_month
        ).exists()


class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="completions")
    date_completed = models.DateField(default=date.today)

    class Meta:
        unique_together = ('habit', 'date_completed')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.habit.last_completed = self.date_completed
        self.habit.save()

class HabitSkip(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="skips")
    date_skipped = models.DateField(default=date.today)
    reason = models.TextField(blank=True)

    class Meta:
        unique_together = ('habit', 'date_skipped')

    def __str__(self):
        return f"{self.habit.name} skipped on {self.date_skipped}"

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_unlocked = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="achievements")

    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    ACHIEVEMENTS = [
    {"name": "New Recruit", "description": "Joined on {date}."},
    {"name": "First Launch", "description": "Complete your first habit."},
    {"name": "Orbit Achiever", "description": "Complete 10 habits."},
    {"name": "Mission Master", "description": "Complete 100 habits."},
    {"name": "Trailblaizer", "description": "Reach a streak of 5."},
    {"name": "Streak of 10", "description": "Reach a streak of 10."},
    {"name": "Master of Momentum", "description": "Reach a streak of 100."},
    {"name": "Bio Uploaded", "description": "Edit your profile for the first time."},
    {"name": "Galactic Observer", "description": "View the leaderboards."},
    {"name": "Progress Tracker", "description": "View your progress."},
]
    
    def unlock_achievement(user, name, description):
        if not Achievement.objects.filter(user=user, name=name).exists():
            Achievement.objects.create(user=user, name=name, description=description, date_unlocked=timezone.now())
    