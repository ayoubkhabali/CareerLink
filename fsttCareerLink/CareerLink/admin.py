# admin.py
from django.contrib import admin
from .models import Student, Enterprise, Professor,Post,Course,Class,Subject
# admin.site.register(User)
admin.site.register(Student)
admin.site.register(Enterprise)
admin.site.register(Professor)
admin.site.register(Post)
admin.site.register(Course)
admin.site.register(Class)
admin.site.register(Subject)

