from django import forms
from .models import Post
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import User,Student, Teacher,Class,Announcement,Assignment
from django.forms.widgets import CheckboxSelectMultiple


class AnnouncementForm(forms.ModelForm):

    class Meta:
        model = Announcement
        fields = ['title', 'content', 'attachment', 'photo']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'cols': 40}),  # Adjust rows and columns as needed
        }

class AssignmentForm(forms.ModelForm):

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date']



class ClassForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.all(), required=False, widget=CheckboxSelectMultiple)

    class Meta:
        model = Class
        fields = ['title', 'description', 'students', 'class_cover']

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
        fields = ['content', 'post_type', 'attachment', 'post_media']  # Add 'post_type' and 'attachment' fields
        widgets = {
            'content': forms.Textarea(attrs={'class': 'main-post', 'placeholder': 'Tell us something...'}),
        }
        labels = {
            'content': '',
            'post_type': 'Post Type',  
            'post_media': 'Media',  # Add label for 'attachment' field
            'attachment': 'Attachment',  # Add label for 'attachment' field
        }


class StudentInfoForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['university', 'major']  # Fields specific to Student model

class TeacherInfoForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['department']  # Fields specific to Student model


class ChangeTeacherInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio','profile_pic','profile_cover']  # Fields specific to User model

class ChangeStudentInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio','profile_pic','profile_cover']  # Fields specific to User model

