from django import forms
from .models import Post
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import User,Student



class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.Role.choices)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'role')

class CustomUserChangeForm(UserChangeForm):
    role = forms.ChoiceField(choices=User.Role.choices)

    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'main-post', 'placeholder': 'tell us something...'}),
        }
        labels = {
            'content': '',  # Set the label for 'content' field to an empty string
        }

class StudentInfoForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['university', 'major']  # Fields specific to Student model

class ChangeStudentInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio']  # Fields specific to User model

