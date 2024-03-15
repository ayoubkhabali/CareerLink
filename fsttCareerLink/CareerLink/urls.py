from django.urls import path
from .views import index
from . import views
from django.http import HttpResponse
from django.contrib.auth import views as auth_views
from django.urls import path



def StudentDashboard(request) :
    return HttpResponse("This is studet dashboard page")

def TeacherDashboard(request) :
    return HttpResponse("This is Teacher dashboard page")


def EntrepriseDashboard(request) :
    return HttpResponse("This is Entreprise dashboard page")

urlpatterns = [
    path('', index, name='index'),
    path('student-dashboard/',StudentDashboard),
    path('teacher-dashboard/',TeacherDashboard),
    path('entreprise-dashboard/',EntrepriseDashboard),
    path('logout/',views.logoutUser,name="logout"),
    path('login/',views.loginPage,name="login"),
    path('rooms/',views.rooms,name="rooms"),


]
