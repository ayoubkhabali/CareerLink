from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Student, User,Post,Like,Comment,SharePost, Follow, Class, Announcement,Assignment
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect,HttpResponseNotAllowed
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .forms import PostForm  # Import the PostForm
from .forms import PostForm, ChangeStudentInfoForm, StudentInfoForm, TeacherInfoForm, ChangeTeacherInfoForm,ClassForm,AnnouncementForm,AssignmentForm

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
    classes_url = request.path == f'/profile/{request.user.username}/classes/'  # Check if the URL corresponds to the about section
    classes = None
   
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

    if request.method == 'POST':
        class_form = ClassForm(request.POST)
        if  class_form.is_valid():
            new_class = form.save(commit=False)
            new_class.teacher = request.user.teacher  # Assuming the user is a teacher
            new_class.save()
            return redirect('user_profile', username=request.user.username)
    else:
        class_form = ClassForm()

    if request.user.role == 'TEACHER' :
        teacher = request.user.teacher
        classes = Class.objects.filter(teacher=teacher).prefetch_related('students')

    elif request.user.role == 'STUDENT':
        student = request.user.student
        classes = Class.objects.filter(students=student).prefetch_related('students')
    
    context = {
        'classes_url' : classes_url,
        'classes' : classes,
        'class_form' : class_form,
        'user': user,
        'form': form,
        'posts': posts,
        'shared_posts': shared_posts,
        'posts_url': posts_url,
        'about_url': about_url  # Pass the about_url variable to the template
    }
    
    return render(request, 'user_profile.html', context)

def create_class(request):

    if request.method == 'POST':
        class_form = ClassForm(request.POST)
        if class_form.is_valid():
            new_class = class_form.save(commit=False)
            new_class.teacher = request.user.teacher
            new_class.save()
            class_form.save_m2m()  # Save many-to-many relationships
            return redirect('user_profile', username=request.user.username)
    else:
        class_form = ClassForm()  # Use the same variable name here
    return render(request, 'create_class.html', {'class_form': class_form})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Class, Announcement
from .forms import AnnouncementForm

from django.contrib.auth.decorators import login_required

@login_required
def class_detail(request, class_id, class_title):
    class_instance = get_object_or_404(Class, pk=class_id)
    class_form = AnnouncementForm()
    assignment_form = AssignmentForm()

    if request.method == 'POST':
        if 'announcement_submit' in request.POST:
            class_form = AnnouncementForm(request.POST, request.FILES)
            if class_form.is_valid():
                announcement = class_form.save(commit=False)
                announcement.class_instance = class_instance
                announcement.save()
                return redirect('class_detail', class_id=class_id, class_title=class_title)
        elif 'assignment_submit' in request.POST:
            assignment_form = AssignmentForm(request.POST, request.FILES)
            if assignment_form.is_valid():
                assignment = assignment_form.save(commit=False)
                assignment.class_instance = class_instance
                assignment.assigned_by = request.user.teacher  # Set the assigned_by field
                assignment.save()
                return redirect('class_detail', class_id=class_id, class_title=class_title)

    announcements = Announcement.objects.filter(class_instance=class_instance).order_by('-created_at')
    assignments = Assignment.objects.filter(class_instance=class_instance).order_by('-created_at')
    context = {
        'class_instance': class_instance,
        'class_form': class_form,
        'assignment_form': assignment_form,
        'announcements': announcements,
        'assignments': assignments
    }
    return render(request, 'class_detail.html', context)


def update_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts_url = request.path == f'/profile/{request.user.username}/'
    about_url = request.path == f'/profile/{request.user.username}/update/'

    if request.method == 'POST':
        if user.role == 'STUDENT':
            user_form = ChangeStudentInfoForm(request.POST, request.FILES, instance=user)
            student_form = StudentInfoForm(request.POST, request.FILES, instance=user.student)
            if user_form.is_valid() and student_form.is_valid():
                user_form.save()
                student_form.save()
                return redirect('user_profile', username=username)
        elif user.role == 'TEACHER':
            user_form = ChangeTeacherInfoForm(request.POST, request.FILES, instance=user)
            teacher_form = TeacherInfoForm(request.POST, request.FILES, instance=user.teacher)
            if user_form.is_valid() and teacher_form.is_valid():
                user_form.save()
                teacher_form.save()
                return redirect('user_profile', username=username)
    else:
        if user.role == 'STUDENT':
            user_form = ChangeStudentInfoForm(instance=user)
            student_form = StudentInfoForm(instance=user.student)
            context = {'user_form': user_form, 'student_form': student_form, 'posts_url': posts_url, 'about_url': about_url}
            return render(request, 'about_profile.html', context)
        elif user.role == 'TEACHER':
            user_form = ChangeTeacherInfoForm(instance=user)
            teacher_form = TeacherInfoForm(instance=user.teacher)
            context = {'user_form': user_form, 'teacher_form': teacher_form, 'posts_url': posts_url, 'about_url': about_url}
            return render(request, 'user_profile.html', context)
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

