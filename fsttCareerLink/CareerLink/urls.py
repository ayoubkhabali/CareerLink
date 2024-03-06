from django.urls import path
from .views import index
from django.http import HttpResponse


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
]
