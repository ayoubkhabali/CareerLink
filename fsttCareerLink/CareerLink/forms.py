from django import forms
from .models import Post
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('professor', 'Professor'),
        ('enterprise', 'Enterprise'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'role')  # Add 'role' field to the form


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']

