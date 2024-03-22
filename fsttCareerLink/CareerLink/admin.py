# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Student, Enterprise, Teacher,Post,Course,Class,Subject,Comment,SharePost, User, Follow
from .forms import CustomUserCreationForm, CustomUserChangeForm

from django.utils.translation import gettext_lazy as _

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'profile_pic', 'profile_cover', 'bio', 'role')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

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
admin.site.register(Follow)


