from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Student, User,Post,Like,Comment,SharePost, Follow
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect,HttpResponseNotAllowed
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .forms import PostForm  # Import the PostForm
from .forms import PostForm, ChangeStudentInfoForm, StudentInfoForm, TeacherInfoForm, ChangeTeacherInfoForm

def aboutUs(request) :
    return render(request,'about_us.html')

def welcome(request) :
     if request.user.is_authenticated:
        return redirect('home')
     else :
        return render(request,'welcome.html')

def home(request):
    user = request.user  # Get the currently logged-in user

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()
            user.posts.add(post)
            return redirect('home')
    else:
        form = PostForm()

    posts = user.posts.all().order_by('-created_at')
    shared_posts = SharePost.objects.filter(user=user)

    return render(request, 'home.html', {'form': form, 'posts': posts, 'user': user, 'shared_posts': shared_posts})

def rooms(request) :
    return render(request,'rooms.html')
# In views.py
@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts_url = request.path == f'/profile/{request.user.username}/'
    about_url = request.path == f'/profile/{request.user.username}/update/'  # Check if the URL corresponds to the about section
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()
            user.posts.add(post)
            return redirect('user_profile', username=username)
    else:
        form = PostForm()
    
    posts = user.posts.all().order_by('-created_at')
    shared_posts = SharePost.objects.filter(user=user)
    
    context = {
        'user': user,
        'form': form,
        'posts': posts,
        'shared_posts': shared_posts,
        'posts_url': posts_url,
        'about_url': about_url  # Pass the about_url variable to the template
    }
    
    return render(request, 'user_profile.html', context)
def update_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts_url = request.path == f'/profile/{request.user.username}/'
    about_url = request.path == f'/profile/{request.user.username}/update/'
    
    if request.user.role == 'STUDENT':
        student = user.student
        if request.method == 'POST':
            user_form = ChangeStudentInfoForm(request.POST, instance=user)
            student_form = StudentInfoForm(request.POST, instance=student)
            if user_form.is_valid() and student_form.is_valid():
                user_form.save()
                student_form.save()
                return redirect('user_profile', username=username)
        else:
            user_form = ChangeStudentInfoForm(instance=user)
            student_form = StudentInfoForm(instance=student)
        context = {'user_form': user_form, 'student_form': student_form, 'posts_url': posts_url, 'about_url': about_url}
        return render(request, 'about_profile.html', context)
    
    elif request.user.role == 'TEACHER':
        teacher = user.teacher
        if request.method == 'POST':
            user_form = ChangeTeacherInfoForm(request.POST, instance=user)
            teacher_form = TeacherInfoForm(request.POST, instance=teacher)
            if user_form.is_valid() and teacher_form.is_valid():
                user_form.save()
                teacher_form.save()
                return redirect('user_profile', username=username)
        else:
            user_form = ChangeTeacherInfoForm(instance=user)
            teacher_form = TeacherInfoForm(instance=teacher)
        context = {'user_form': user_form, 'teacher_form': teacher_form, 'posts_url': posts_url, 'about_url': about_url}
        return render(request, 'user_profile.html', context)
    
    else:
        return render(request, 'user_profile.html', {'posts_url': posts_url, 'about_url': about_url})

from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def follow_user(request, username):
    user_to_follow = User.objects.get(username=username)
    request.user.following.add(user_to_follow)
    user_to_follow.followers.add(request.user)
    return redirect('user_profile', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = User.objects.get(username=username)
    request.user.following.remove(user_to_unfollow)
    user_to_unfollow.followers.remove(request.user)
    return redirect('user_profile', username=username)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'home.html')


def logoutUser(request):
    logout(request)
    return redirect('/')


from django.shortcuts import redirect
from django.http import JsonResponse


# views.py

from django.shortcuts import redirect, get_object_or_404
from .models import Post, Like

def like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    
    # Check if the user has already liked the post
    existing_like = Like.objects.filter(post=post, user=user).first()
    if existing_like:
        # If the user already liked the post, remove the like
        existing_like.delete()
        # Decrement the likes count in the Post model
        post.likes -= 1
        post.save()
    else:
        # If the user hasn't liked the post, create a new like instance
        like = Like(post=post, user=user)
        like.save()
        # Increment the likes count in the Post model
        post.likes += 1
        post.save()
    
    # Redirect back to the homepage
    return redirect(request.META.get('HTTP_REFERER', '/'))


def comment_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Create a new comment instance
            comment = Comment(post=post, author=request.user, content=content)
            comment.save()
    
    # Redirect back to the homepage
    return redirect('home')

def share_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    # Create a new instance of the SharePost model
    share_post_instance = SharePost.objects.create(
        post=post,
        user=request.user
    )
    
    # Redirect back to the homepage
    return redirect('home')

def profile(request):
    posts = None 
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    shared_posts = SharePost.objects.filter(user=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            request.user.posts += 1
            return redirect('profile')  # Redirect to the homepage after publishing
    else:
        form = PostForm()
    return render(request, 'profile.html', {'shared_posts': shared_posts,'posts' : posts, 'form':form})


def student_profile(request):
    student = None
    posts = None

    try:
        student = Student.objects.get(user=request.user)
        posts = Post.objects.filter(author=request.user).order_by('-created_at')
        
    except Student.DoesNotExist:
        pass

    return render(request, 'student_profile.html', {'student': student, 'posts': posts})

