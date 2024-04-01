from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.postgres.fields import ArrayField
from datetime import datetime,timezone
import uuid

from datetime import date

class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'admin'
        STUDENT = "STUDENT", "student"
        TEACHER = "TEACHER", "teacher"
        ENTERPRISE = "ENTERPRISE", "enterprise"
    base_role = Role.ADMIN
    role = models.CharField(max_length=50, choices=Role.choices)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=50, default= '')
    posts = models.ManyToManyField('Post', related_name='authors')
    followers = models.ManyToManyField('self', related_name='user_followers_set', symmetrical=False)
    following = models.ManyToManyField('self', related_name='user_following_set', symmetrical=False)
    profile_pic = models.FileField(upload_to='media/', null=True, blank=True, default='media/default_profile_pic.jpg')
    profile_cover = models.FileField(upload_to='media/', null=True, blank=True, default='media/default_profile_cover.jpg')
    birth_date = models.DateField(default=date(2000, 1, 1))
    country = models.CharField(max_length=50, default='undefined')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,default='M')




    def save(self, *args, **kwargs):
        creating = not self.pk
        if creating and self.role == User.Role.STUDENT:
            super().save(*args, **kwargs)
            Student.objects.create(user=self, university='University Name', major='Major Name')
        elif creating and self.role == User.Role.TEACHER:
            super().save(*args, **kwargs)
            Teacher.objects.create(user=self,  department = "Department Name")
        elif creating and self.role == User.Role.ENTERPRISE:
            super().save(*args, **kwargs)
            Enterprise.objects.create(user=self, company_name="Company Name")
        else:
            super().save(*args, **kwargs)



class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    CNE = models.CharField(max_length=20,primary_key = True) 
    university = models.CharField(max_length=20, default='')
    major = models.CharField(max_length=20, default='')
    projects = models.FileField(upload_to='studentProjects/', null=True, blank=True)


    def save(self, *args, **kwargs):
        # Generate a unique student_id if it's not already set
        if not self.CNE:
            self.CNE = self.generate_unique_student_id()
        super().save(*args, **kwargs)


    def generate_unique_student_id(self):
        # Fetch the latest student ID from the database
        last_student = Student.objects.order_by('-CNE').first()
        if last_student:
            last_id = int(last_student.CNE[1:])  # Extract numerical part
            new_id = last_id + 1
        else:
            new_id = 1
        # Generate the new student ID with the desired format
        return f'P{new_id:08d}'  # Example: P13424563


    def __str__(self):
        return self.user.username


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default='')
    department = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.user.username


class Enterprise(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default='')
    company_name = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.user.username


class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()

class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skills = models.CharField(max_length=100)

class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()

class Interest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interests = models.CharField(max_length=100)

class ContactInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()



class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    type = models.CharField(max_length=50, default="normal") 
    def __str__(self):
        return f'Notification from {self.sender.username} to {self.receiver.username}'



class Post(models.Model):
    class PostType(models.TextChoices):
        PEDAGOGICAL = "PEDAGOGICAL", "Activités pédagogiques"
        RESEARCH = "RESEARCH", "Activités de recherche"
        REGULAR = "REGULAR", "Regular Post"

    id = models.AutoField(primary_key=True, serialize=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    post_media = models.FileField(upload_to='posts-files/', null=True, blank=True)  # Add attachment field
    attachment = models.FileField(upload_to='posts-files/', null=True, blank=True)  # Add attachment field
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    post_type = models.CharField(max_length=50, choices=PostType.choices, default=PostType.REGULAR)

class Comment(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")  # Custom related_name
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Follow(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_following')
    followed_account = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_followers')

class SharePost(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shared_posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} shared {self.post.id}"




class Class(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    title = models.CharField(max_length=100)
    description = models.TextField(default='')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student, related_name='classes')
    class_cover = models.FileField(upload_to='media/', null=True, blank=True, default='media/default_profile_cover.jpg')

class Exam(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, default=None)  # Specify a default value
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField()


class Question(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)

class Answer(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

class StudentAnswer(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    correct_answers_count = models.IntegerField(default=0)


class Announcement(models.Model):
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    attachment = models.FileField(upload_to='announcement_attachments/', null=True, blank=True)
    photo = models.ImageField(upload_to='announcement_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

from django.utils import timezone


class Assignment(models.Model):
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True, serialize=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    attachment = models.FileField(upload_to='announcement_attachments/', null=True, blank=True)
    assigned_by = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
    
class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    submission_file = models.FileField(upload_to='assignment_submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username}'s submission for {self.assignment.title}"
    


    
class ChatMessage(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']



class Offer(models.Model):
    class Type(models.TextChoices):
        JOB = 'job', 'Job'
        INTERNSHIP = 'internship', 'Internship'

    type = models.CharField(max_length=20, choices=Type.choices)
    offer_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    skills_required = models.CharField(max_length=200)
    location = models.CharField(max_length=200, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers_created')
    salary = models.FloatField(default=0.00)

    def __str__(self):
        return self.title
    
class Application(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    cv = models.FileField(upload_to='applications/cv/')
    cover_letter = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Application for {self.offer.title} by {self.applicant.username}'