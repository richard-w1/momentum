from django import forms
from .models import Habit
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import custom_user

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'frequency', 'experience', 'custom_experience', 'reminder_time', 'reminder_weekly', 'reminder_monthly']
    
        help_texts = {
        'reminder_time': "HH:MM in 24 hr format",
    }

    def save(self, commit=True, user=None):
        habit = super().save(commit=False)
        if user:
            habit.user = user
        if commit:
            habit.save()
        return habit

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
    )

    class Meta:
        #model is user because django's default auth expects a user model
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    #creating a instance of custom_user
    def save(self, commit=True):
        user = super().save(commit=True)
        
        user_profile = custom_user(
            user=user,
            birth_date=self.cleaned_data.get('birth_date')
        )
        if commit:
            user_profile.save()
        
        return user
    
class EditUserProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    password = forms.CharField(widget=forms.HiddenInput(), required=False)

class EditCustomUserProfileForm(forms.ModelForm):
    class Meta:
        model = custom_user
        fields = ['birth_date', 'bio', 'rank']

    def __init__(self, *args, **kwargs):
        super(EditCustomUserProfileForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        if instance:
            available_ranks = []
            for milestone_level, rank_title, _, _ in instance.rank_milestones:
                if instance.level >= milestone_level:
                    available_ranks.append((rank_title, rank_title))
            
            self.fields['rank'].choices = available_ranks