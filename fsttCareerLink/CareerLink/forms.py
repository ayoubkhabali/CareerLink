from django import forms
from .models import Post
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import User,Student, Teacher,Class,Announcement,Assignment,AssignmentSubmission, Exam,Question,Answer, ChatMessage, Offer, Application
from django.forms.widgets import CheckboxSelectMultiple
from datetime import date




from django import forms
from .models import Education, Skill, Experience, Interest, ContactInfo


# forms.py
from django.contrib.auth.forms import PasswordChangeForm

class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'start_date', 'end_date', 'description']
class ChangeEducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'start_date', 'end_date', 'description']


class SkillsForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['skills']


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['title', 'company', 'start_date','end_date','description']

class InterestForm(forms.ModelForm):
    class Meta:
        model = Interest
        fields = ['interests']

class ContactInfoForm(forms.ModelForm):
    class Meta:
        model = ContactInfo
        fields = ['address','phone_number','email']








class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'send a message...'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].label = ''

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['exam_date', 'start_time', 'end_time', 'description']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['answer_text', 'is_correct']

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submission_file']


class AnnouncementForm(forms.ModelForm):

    class Meta:
        model = Announcement
        fields = ['title', 'content', 'attachment', 'photo']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'cols': 40}),  # Adjust rows and columns as needed
        }

from django.utils import timezone

class AssignmentForm(forms.ModelForm):

    class Meta:
        model = Assignment
        fields = ['title', 'description','due_date','attachment']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


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
            'attachment': forms.FileInput(attrs={'class': 'attachment-post'}),
            'post_media': forms.FileInput(attrs={'class': 'media-post'}),
        
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
        fields = ['username', 'email', 'first_name', 'last_name', 'bio', 'profile_pic', 'profile_cover']
        widgets = {
            'profile_pic': forms.FileInput(attrs={'class': 'profile-pic'}),
            'profile_cover': forms.FileInput(attrs={'class': 'profile-cover'}),
        
        }

class ChangeStudentInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio','profile_pic','profile_cover']  # Fields specific to User model
        widgets = {
                'profile_pic': forms.FileInput(attrs={'class': 'profile-pic'}),
                'profile_cover': forms.FileInput(attrs={'class': 'profile-cover'}),
            
            }

class CreateOffer(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['type', 'title', 'description', 'skills_required','location','salary']

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cv', 'cover_letter']

