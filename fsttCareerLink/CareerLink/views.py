from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Student, User,Post
from .forms import PostForm
from django.contrib.auth.decorators import login_required




from .forms import PostForm  # Import the PostForm

def aboutUs(request) :
    return render(request,'about_us.html')

def welcome(request) :
     if request.user.is_authenticated:
        return redirect('home')
     else :
        return render(request,'welcome.html')

def home(request):
    student = None  # Initialize student variable
    posts = None  # Initialize posts variable
    
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        pass  # If student doesn't exist, keep student as None
    
    # Fetch all posts, ordered by creation date
    posts = Post.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')  # Redirect to the homepage after publishing
    else:
        form = PostForm()

    return render(request, 'home.html', {'student': student, 'form': form, 'posts': posts})


def rooms(request) :
    return render(request,'rooms.html')

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User doesn't exist.")
            return redirect('home')  # Redirect back to login page if user doesn't exist

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password is incorrect.')

    return render(request, 'home.html')

def logoutUser(request):
    logout(request)
    return redirect('/')


def student_profile(request):
    try:
        student = Student.objects.get(user=request.user)
        return render(request, 'student_profile.html', {'student': student})
    except Student.DoesNotExist:
        return render(request, 'student_profile.html', {'student': None})