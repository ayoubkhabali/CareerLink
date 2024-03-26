from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.postgres.fields import ArrayField
from datetime import datetime,timezone
import uuid


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'admin'
        STUDENT = "STUDENT", "student"
        TEACHER = "TEACHER", "teacher"
        ENTERPRISE = "ENTERPRISE", "enterprise"
    
    base_role = Role.ADMIN
    role = models.CharField(max_length=50, choices=Role.choices)
    bio = models.TextField(blank=True)
    posts = models.ManyToManyField('Post', related_name='authors')
    followers = models.ManyToManyField('self', related_name='user_followers_set', symmetrical=False)
    following = models.ManyToManyField('self', related_name='user_following_set', symmetrical=False)
    profile_pic = models.FileField(upload_to='media/', null=True, blank=True, default='media/default_profile_pic.jpg')
    profile_cover = models.FileField(upload_to='media/', null=True, blank=True, default='media/default_profile_cover.jpg')

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
    likes = models.IntegerField(default=0)
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

class Subject(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Course(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    subjects = models.ManyToManyField(Subject, related_name='courses')
    studentsList = models.ManyToManyField(Student,related_name='studentLists')
    

    def __str__(self):
        return self.name

class Exam(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField()

class Class(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    title = models.CharField(max_length=100)
    description = models.TextField(default='')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student, related_name='classes')
    class_cover = models.FileField(upload_to='media/', null=True, blank=True, default='media/default_profile_cover.jpg')



class Announcement(models.Model):
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    attachment = models.FileField(upload_to='announcement_attachments/', null=True, blank=True)
    photo = models.ImageField(upload_to='announcement_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Assignment(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    associated_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    

    
class ChatMessage(models.Model):
    id = models.AutoField(primary_key=True, serialize=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']