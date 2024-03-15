from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from datetime import datetime

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20)
    # Define relationships with other entities like courses and announcements

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professor_profile')
    department = models.CharField(max_length=100)
    # Define relationships with courses and announcements
    office_location = models.CharField(max_length=200)

class Enterprise(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='enterprise_profile')
    company_name = models.CharField(max_length=100)
    job_offers_posted = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    internship_offers_posted = ArrayField(models.CharField(max_length=100), blank=True, default=list)


class Course(models.Model):
    course_id = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    description = models.TextField()
    syllabus_documents = models.FileField(upload_to='uploads/')  # Use FileField for file uploads
    teaching_materials = ArrayField(models.CharField(max_length=100), blank=True)
    assignments = models.TextField()

class Exam(models.Model):
    exam_id = models.CharField(max_length=20)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=datetime.now, verbose_name='Exam Date')  # Use default=datetime.now
    duration = models.IntegerField()
    grade = models.FloatField()

class Announcement(models.Model):
    announcement_id = models.CharField(max_length=20)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField()
    timestamp = models.DateTimeField(default=datetime.now, verbose_name='Time Stamp')  # Use default=datetime.now

class Material(models.Model):
    material_id = models.CharField(max_length=20)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    material_type = models.CharField(max_length=50)
    material_link = models.CharField(max_length=50)

class Post(models.Model) :
    post_id = models.CharField(max_length=20)
    author_id = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.TextField()
    time_stamp = models.DateTimeField(default=datetime.now, verbose_name='post Date')
    post_comments = ArrayField(models.CharField(max_length=100), blank=True)
    post_likes = ArrayField(models.CharField(max_length=100), blank=True)

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)  # AutoField for automatically generated IDs
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message_content = models.TextField()
    time_stamp = models.DateTimeField(default=datetime.now, verbose_name='message Date')



class Like(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_posts')
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    time_stamp = models.DateTimeField(default=datetime.now, verbose_name='like Date')

class Comment(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment_content = models.TextField()
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    time_stamp = models.DateTimeField(default=datetime.now, verbose_name='comment Date')
