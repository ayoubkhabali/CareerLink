# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Student, Enterprise, Teacher,Post,Course,Class,Subject,Comment,SharePost, User
from .forms import CustomUserCreationForm, CustomUserChangeForm

from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )


admin.site.register(User, CustomUserAdmin)




admin.site.register(Student)
admin.site.register(Enterprise)
admin.site.register(Teacher)
admin.site.register(Post)
admin.site.register(Course)
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(Comment)
admin.site.register(SharePost)


