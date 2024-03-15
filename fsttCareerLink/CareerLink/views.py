from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User


def index(request):
    return render(request, 'home.html')


def rooms(request) :
    return render(request,'rooms.html')

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User doesn't exist.")
            return redirect('/')  # Redirect back to login page if user doesn't exist

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Username or password is incorrect.')

    return render(request, 'home.html')


def logoutUser(request):
    logout(request)
    return redirect('/')
# Create your views here.
