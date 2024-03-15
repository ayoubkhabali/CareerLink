# admin.py
from django.contrib import admin
from .models import Student, Enterprise, Professor

# admin.site.register(User)
admin.site.register(Student)
admin.site.register(Enterprise)
admin.site.register(Professor)
