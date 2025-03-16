from django import forms
from .models import Habit
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import custom_user

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'frequency']
    
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