from django.urls import path
from .views import home
from . import views
from django.http import HttpResponse
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView


def StudentDashboard(request) :
    return HttpResponse("This is studet dashboard page")

def TeacherDashboard(request) :
    return HttpResponse("This is Teacher dashboard page")


def EntrepriseDashboard(request) :
    return HttpResponse("This is Entreprise dashboard page")

urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.welcome, name='welcome'),
    path('about_us', views.aboutUs, name='about'),
    path('student-dashboard/',StudentDashboard),
    path('teacher-dashboard/',TeacherDashboard),
    path('entreprise-dashboard/',EntrepriseDashboard),
    path('logout/',views.logoutUser,name="logout"),
    path('login/',views.loginPage,name="login"),
    path('rooms/',views.rooms,name="rooms"),
    path('student_profile/',views.student_profile,name="student_profile"),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.comment_post, name='comment_post'),
    path('share/<int:post_id>/', views.share_post, name='share_post'),
    path('profile/', views.profile, name='profile'),
    path('profile/about/', views.profile, name='profile-edit'),
    path('profile/<str:username>', RedirectView.as_view(url='/profile/%(username)s/')),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('update_profile/', views.update_profile, name='update_profile'),



]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
