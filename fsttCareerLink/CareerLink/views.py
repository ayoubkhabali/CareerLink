from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Student, User,Post,Like,Comment,SharePost, Follow, Class, Announcement,Assignment,AssignmentSubmission
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect,HttpResponseNotAllowed
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .forms import PostForm  # Import the PostForm
from .forms import PostForm, ChangeStudentInfoForm, StudentInfoForm, TeacherInfoForm, ChangeTeacherInfoForm,ClassForm,AnnouncementForm,AssignmentForm,AssignmentSubmissionForm

from django.template.loader import render_to_string
from django.http import JsonResponse



def search_users(request):
    # Get the search query from the AJAX request
    query = request.GET.get('query', '')

    # Perform the search query on the User model
    users = User.objects.filter(username__icontains=query)

    # Render the search results template with the users
    return render(request, 'search_results.html', {'users': users})



def search_students(request):
    # Get the search query from the AJAX request
    query = request.GET.get('query', '')

    # Perform the search query on the User model
    students = Student.objects.filter(user__username__icontains=query)

    # Render the search results template with the users
    return render(request, 'search_students_results.html', {'students': students})





def aboutUs(request) :
    return render(request,'about_us.html')

def welcome(request) :
     if request.user.is_authenticated:
        return redirect('home')
     else :
        return render(request,'welcome.html')
     
from django.db.models import Q
from django.db.models import Subquery, OuterRef

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

    # Get the latest message ID for each conversation involving the current user
    latest_message_ids = Subquery(
        ChatMessage.objects.filter(
            Q(sender=OuterRef('pk'), receiver=user) |
            Q(sender=user, receiver=OuterRef('pk'))
        ).order_by('-timestamp').values('id')[:1]
    )
    
    # Annotate each user with the ID of the latest message from/to the current user
    users_with_messages = User.objects.exclude(id=user.id).annotate(
        latest_message_id=latest_message_ids
    )
    
    # Select the actual message content and sender based on the annotated message ID
    for user_with_message in users_with_messages:
        latest_message_id = user_with_message.latest_message_id
        if latest_message_id:
            latest_message = ChatMessage.objects.get(id=latest_message_id)
            user_with_message.latest_message = latest_message
            if latest_message.sender != user:
                user_with_message.profile_pic_url = latest_message.sender.profile_pic.url
            else:
                user_with_message.profile_pic_url = latest_message.receiver.profile_pic.url
        else:
            user_with_message.latest_message = None
            user_with_message.profile_pic_url = None

    # Filter follow requests for the current user
    follow_requests = Notification.objects.filter(receiver=user, type='follow_request')

    return render(request, 'home.html', {'form': form, 'posts': posts, 'user': user, 'shared_posts': shared_posts, 'users_with_messages': users_with_messages, 'follow_requests': follow_requests})



from .forms import EducationForm, SkillsForm, ExperienceForm, InterestForm, ContactInfoForm

@login_required  # Apply login_required decorator to ensure only logged-in users can access these views
def add_education(request, username):
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            # Assign the current logged-in user to the submitted data
            education = form.save(commit=False)
            education.user = request.user
            education.save()
            return redirect('user_profile', username)  # Replace with your success URL
    else:
        form = EducationForm()
    return render(request, 'add_education.html', {'form': form})


def add_experience(request, username):
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            # Assign the current logged-in user to the submitted data
            experience = form.save(commit=False)
            experience.user = request.user
            experience.save()
            return redirect('user_profile', username)  # Replace with your success URL
    else:
        form = ExperienceForm()
    return render(request, 'add_experience.html', {'form': form})


from django.forms import formset_factory
def add_interest_skill(request, username):
    SkillsFormSet = formset_factory(SkillsForm, extra=1)
    InterestFormSet = formset_factory(InterestForm, extra=1)

    if request.method == 'POST':
        skills_formset = SkillsFormSet(request.POST, prefix='skills')
        interest_formset = InterestFormSet(request.POST, prefix='interest')

        if skills_formset.is_valid() and interest_formset.is_valid():
            for skills_form in skills_formset:
                skill = skills_form.save(commit=False)
                skill.user = request.user
                skill.save()

            for interest_form in interest_formset:
                interest = interest_form.save(commit=False)
                interest.user = request.user
                interest.save()

            return redirect('user_profile', username)  # Replace with your success URL
    else:
        skills_formset = SkillsFormSet(prefix='skills')
        interest_formset = InterestFormSet(prefix='interest')

    return render(request, 'add_interest_skill.html', {
        'skills_formset': skills_formset,
        'interest_formset': interest_formset,
    })

def add_contact(request, username):
    if request.method == 'POST':
        form = ContactInfoForm(request.POST)
        if form.is_valid():
            # Assign the current logged-in user to the submitted data
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            return redirect('user_profile', username)  # Replace with your success URL
    else:
        form = ContactInfoForm()
    return render(request, 'add_contact.html', {'form': form})


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

def assignment_detail(request, class_id, class_title, assignment_id):
    class_instance = get_object_or_404(Class, pk=class_id)
    assignment = get_object_or_404(Assignment, pk=assignment_id)


    if request.method == 'POST':
        assign_submit_form = AssignmentSubmissionForm(request.POST, request.FILES)
        if assign_submit_form.is_valid():
            assign_submit = assign_submit_form.save(commit=False)
            assign_submit.assignment = assignment
            assign_submit.student = request.user
            assign_submit.save()
            return redirect('assignment_detail', class_id=class_id, class_title=class_title, assignment_id=assignment_id)
    else:
        assign_submit_form = AssignmentSubmissionForm()
    
    if request.user.role == 'STUDENT':
        # Filter submissions by the current student
        my_submissions = AssignmentSubmission.objects.filter(student=request.user, assignment=assignment)
    else:
        my_submissions = None


    assignment_submissions = AssignmentSubmission.objects.filter(assignment=assignment)

    context = {
        'class_instance': class_instance, 'assignment': assignment, 'assign_submit_form': assign_submit_form,
        'assignment_submissions' : assignment_submissions, 'my_submissions': my_submissions}
    return render(request, 'assignment_detail.html', context)

def unsubmit_assignment(request, class_id, class_title, assignment_id):
    assignment_submission = get_object_or_404(AssignmentSubmission, student=request.user, assignment_id=assignment_id)
    assignment_submission.delete()
    # Redirect back to the assignment detail page
    return redirect('assignment_detail', class_id=class_id, class_title=class_title, assignment_id=assignment_id)

from .models import Exam, Question, Answer

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Class, Exam


from .forms import ExamForm, QuestionForm, AnswerForm
def create_exam(request, class_id, class_title):
    # Retrieve the class instance
    class_instance = get_object_or_404(Class, pk=class_id)

    if request.method == 'POST':
        exam_form = ExamForm(request.POST)
        question_forms = [QuestionForm(request.POST, prefix=str(i)) for i in range(3)]
        answer_forms = [[AnswerForm(request.POST, prefix=f'answer-{i}-{j}') for j in range(3)] for i in range(3)]

        if exam_form.is_valid() and all([q.is_valid() for q in question_forms]) and all([all([a.is_valid() for a in ans]) for ans in answer_forms]):
            exam = exam_form.save(commit=False)
            exam.class_instance = class_instance  # Assign the class instance to the exam
            exam.professor = request.user
            exam.save()

            for question_form, answer_set in zip(question_forms, answer_forms):
                question = question_form.save(commit=False)
                question.exam = exam
                question.save()

                for answer_form in answer_set:
                    answer = answer_form.save(commit=False)
                    answer.question = question
                    answer.save()

                return redirect('exam_detail', class_id=class_id, class_title=class_title, exam_id=exam.id)
    else:
        exam_form = ExamForm()
        question_forms = [QuestionForm(prefix=str(i)) for i in range(3)]
        answer_forms = [[AnswerForm(prefix=f'answer-{i}-{j}') for j in range(3)] for i in range(3)]

    question_and_answer_forms = zip(question_forms, answer_forms)

    return render(request, 'create_exam.html', {
        'class_id': class_id,
        'class_title': class_title,
        'exam_form': exam_form,
        'question_and_answer_forms': question_and_answer_forms,
    })

def exam_detail(request,  class_id, class_title,exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    return render(request, 'exam_detail.html', {'exam': exam, 'class_id' : class_id,'class_title' : class_title})






from .models import ChatMessage
from django.db.models import Max

from django.db.models import Q


from django.shortcuts import render, get_object_or_404
from .models import ChatMessage, User

from django.db.models import Q, Max, OuterRef, Subquery
from .models import ChatMessage, User
def inbox(request):
    # Get the latest message ID for each conversation involving the current user
    latest_message_ids = Subquery(
        ChatMessage.objects.filter(
            Q(sender=OuterRef('pk'), receiver=request.user) |
            Q(sender=request.user, receiver=OuterRef('pk'))
        ).order_by('-timestamp').values('id')[:1]
    )
    
    # Annotate each user with the ID of the latest message from/to the current user
    users = User.objects.exclude(id=request.user.id).annotate(
        latest_message_id=latest_message_ids
    )
    
    # Select the actual message content and sender based on the annotated message ID
    for user in users:
        latest_message_id = user.latest_message_id
        if latest_message_id:
            latest_message = ChatMessage.objects.get(id=latest_message_id)
            user.latest_message = latest_message
            if latest_message.sender != request.user:
                user.profile_pic_url = latest_message.sender.profile_pic.url
            else:
                user.profile_pic_url = latest_message.receiver.profile_pic.url
        else:
            user.latest_message = None
            user.profile_pic_url = None
    
    return render(request, 'inbox.html', {'users': users})



from .forms import ChatMessageForm


def conversation_detail(request, receiver_id):
    sender = request.user
    receiver = get_object_or_404(User, pk=receiver_id)  # Define 'receiver' here
    messages = ChatMessage.objects.filter(sender=sender, receiver=receiver) | ChatMessage.objects.filter(sender=receiver, receiver=sender)
    messages = messages.order_by('timestamp')

    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = sender
            new_message.receiver = receiver
            new_message.save()
            # Redirect to the same conversation view to display the new message
            return redirect('conversation_detail', receiver_id=receiver_id)
    else:
        form = ChatMessageForm()

    return render(request, 'conversation_detail.html', {'messages': messages, 'receiver': receiver, 'form': form})




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
from .models import Notification

User = get_user_model()

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    # Create a follow request notification
    Notification.objects.create(
        sender=request.user,
        receiver=user_to_follow,
        message=f'{request.user.username} wants to follow you.',
        type='follow_request',  # Set the type to 'follow_request'
    )
    return redirect('user_profile', username=username)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


def accept_follow_request(request, username):
    # Get the user sending the follow request
    user_to_accept = get_object_or_404(User, username=username)
    
    # Add user_to_accept to the current user's following list
    request.user.following.add(user_to_accept)
    
    # Optionally, you may want to add the current user to the follower list of user_to_accept
    user_to_accept.followers.add(request.user)
    
    # Delete the follow request notification
    Notification.objects.filter(sender=user_to_accept, receiver=request.user, type='follow_request').delete()
    
    return redirect('home')

def refuse_follow_request(request, username):
    # Get the user sending the follow request
    user_to_refuse = get_object_or_404(User, username=username)
    
    # Delete the follow request notification
    Notification.objects.filter(sender=user_to_refuse, receiver=request.user, type='follow_request').delete()
    
    return redirect('home')



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

