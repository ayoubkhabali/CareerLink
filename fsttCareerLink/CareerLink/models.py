from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.postgres.fields import ArrayField
from datetime import datetime


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'admin'
        STUDENT = "STUDENT", "student"
        TEACHER = "TEACHER", "teacher"
        ENTERPRISE = "ENTERPRISE", "enterprise"
    
    base_role = Role.ADMIN
    role = models.CharField(max_length=50, choices=Role.choices)
    bio = models.TextField(blank=True)
    posts = models.IntegerField(default=0)
    followers = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
    profile_pic = models.FileField(upload_to='profilePics/', null=True, blank=True)
    profile_cover = models.FileField(upload_to='profileCovers/', null=True, blank=True)

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
    student_id = models.AutoField(primary_key=True, serialize=False)
    university = models.CharField(max_length=20, default='')
    major = models.CharField(max_length=20, default='')
    projects = models.FileField(upload_to='studentProjects/', null=True, blank=True)



class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default='')
    department = models.CharField(max_length=100, default='')


class Enterprise(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default='')
    company_name = models.CharField(max_length=100, default='')

class Post(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    attachement = models.FileField(upload_to='posts-files/', null=True, blank=True)
    likes = models.IntegerField(default=0)  # Remove related_name="like"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")  # Custom related_name
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    followed_account = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')

class SharePost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shared_posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} shared {self.post.id}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    subjects = models.ManyToManyField(Subject, related_name='courses')
    studentsList = models.ManyToManyField(Student,related_name='studentLists')
    

    def __str__(self):
        return self.name

class Exam(models.Model):
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100)
    description = models.TextField()

class Class(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student, related_name='classes')




class Assignment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    associated_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    

    
class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']