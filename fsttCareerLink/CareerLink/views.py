from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Student, User,Post,Like,Comment,SharePost, Follow, Class, Announcement,Assignment,AssignmentSubmission, Offer, Application, Education, Teacher,Enterprise
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect,HttpResponseNotAllowed
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .forms import PostForm  # Import the PostForm
from .forms import PostForm, ChangeStudentInfoForm, StudentInfoForm, TeacherInfoForm, ChangeTeacherInfoForm,ClassForm,AnnouncementForm,AssignmentForm,AssignmentSubmissionForm, CreateOffer,ApplicationForm,ChangeEducationForm, ChangeEnterpriseInfoForm, EnterpriseInfoForm,UserForm
from .forms import SignUpForm
from django.template.loader import render_to_string
from django.http import JsonResponse


def followers_view(request,username) :
    user = get_object_or_404(User, username=username)
    followers = user.followers.all()
    following = user.following.all()
    return render(request, 'followers_following.html', {'user': user, 'followers': followers, 'following': following})

def signup_success(request):
    return render(request, 'signup_success.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate the user until approved by admin
            user.save()
            
            # Notify admin
            admin = User.objects.filter(role=User.Role.ADMIN).first()  # You need to fetch the admin user
            if admin:
                notification = Notification.objects.create(
                    sender=user,
                    receiver=admin,
                    message=f"New user '{user.username}' signed up and requires approval."
                )
                messages.success(request, "Your account has been created. Please wait for admin approval.")
            else:
                messages.error(request, "Admin user not found. Cannot send approval request.")

            return redirect('signup_success')  # Redirect to signup success page
    else:
        form = SignUpForm()
    return render(request, 'authentification.html', {'form': form})

def search_users(request):
    # Get the search query from the AJAX request
    query = request.GET.get('query', '')

    # Perform the search query on the User model
    users = User.objects.filter(username__icontains=query)

    # Render the search results template with the users
    return render(request, 'search_results.html', {'users': users})



def search_students(request):
    query = request.GET.get('query', '')

    students = Student.objects.filter(user__username__icontains=query)

    return render(request, 'search_students_results.html', {'students': students})



def video_lecture(request,class_id, class_title) :
    class_instance = get_object_or_404(Class, pk=class_id)

    
    # if not (request.user.role == User.Role.STUDENT or request.user.role == User.Role.TEACHER):
    #     raise Http404("You are not authorized to view this page.")

    if not (class_instance.teacher.user == request.user or request.user in class_instance.students.all()):
        raise Http404("You are not authorized to view this page.")


    return render(request,'lecture.html', {'name' : request.user.username})


def admin_dashboard(request) :
    users = User.objects.all()
    students = Student.objects.all()
    teachers = Teacher.objects.all()
    enterprises = Enterprise.objects.all()
    posts = Post.objects.all()
    classes = Class.objects.all()
    offers = Post.objects.all()
    admin = User.objects.filter(role=User.Role.ADMIN).first()  # Fetch admin user
    admin_notifications = Notification.objects.filter(receiver=admin, read=False) if admin else []



    if request.method == 'POST':
            add_form = SignUpForm(request.POST)
            if add_form.is_valid():
                new_user = add_form.save()
                return redirect('admin_dashboard') 
    else:
        add_form = SignUpForm()


    context = {
        'users': users,
        'students' : students,
        'teachers' :teachers,
        'enterprises' : enterprises,
        'posts' : posts,
        'classes' : classes,
        'offers' :offers,
        'add_form' : add_form,
        'admin_notifications': admin_notifications,

               }

    return render(request, 'admin_dashboard.html', context)

def approve_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_approved = True
    user.is_active = True  # Activate the user upon approval
    user.save()

    admin = User.objects.filter(role=User.Role.ADMIN).first()
    if admin:
        notification = Notification.objects.filter(sender=user, receiver=admin).first()
        if notification:
            notification.delete()
    return redirect('admin_dashboard')

def reject_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()  # Or any other action you want to take upon rejection
    return redirect('admin_dashboard')

def aboutUs(request) :
    return render(request,'about_us.html')

def welcome(request) :
     if request.user.is_authenticated:
        return redirect('home')
     else :
        return render(request,'welcome.html')
     
from django.db.models import Q
from django.db.models import Subquery, OuterRef
from .forms import SendMessageForm


@login_required
def home(request):
    user = request.user  # Get the currently logged-in user

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  
        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()
            user.posts.add(post)
            return redirect('home')
    else:
        form = PostForm()


    if request.method == 'POST':
        send_form = SendMessageForm(request.POST)
        if send_form.is_valid():
            message = send_form.save(commit=False)
            message.sender = user  # Set the sender to the current user
            message.save()
            return redirect('home')
    else:
        send_form = SendMessageForm()

    followed_users = user.following.all()
    posts = Post.objects.filter(Q(author=user) | Q(author__in=followed_users)).order_by('-created_at')
    shared_posts = SharePost.objects.filter(user=user)

    # Get the latest message ID for each conversation involving the current user
    latest_message_ids = Subquery(
        ChatMessage.objects.filter(
            Q(sender=user, receiver=OuterRef('pk')) | Q(sender=OuterRef('pk'), receiver=user)
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

    return render(request, 'home.html', {'form': form, 'posts': posts, 'user': user, 'shared_posts': shared_posts, 'users_with_messages': users_with_messages, 'follow_requests': follow_requests, 'send_form' : send_form})


def delete_post(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(pk=post_id)
        # Check if the user is authorized to delete the post (optional)
        if post.author == request.user:
            post.delete()
    return redirect('home')


from .forms import EducationForm, SkillsForm, ExperienceForm, ContactInfoForm

@login_required  # Apply login_required decorator to ensure only logged-in users can access these views
def add_education(request, username):
    if request.method == 'POST':
        education_form = EducationForm(request.POST)
        if education_form.is_valid():
            education, created = Education.objects.get_or_create(user=request.user)
            education.institution = education_form.cleaned_data['institution']
            education.degree = education_form.cleaned_data['degree']
            education.field_of_study = education_form.cleaned_data['field_of_study']
            education.start_date = education_form.cleaned_data.get('start_date')  # Nullable start_date
            education.end_date = education_form.cleaned_data['end_date']
            education.save()
            return redirect('user_profile', username)
    else:
        previous_education = Education.objects.filter(user=request.user).first()
        education_form = EducationForm(instance=previous_education)
    return render(request, 'add_education.html', {'education_form': education_form})


def add_experience(request, username):
    if request.method == 'POST':
        experience_form = ExperienceForm(request.POST)
        if experience_form.is_valid():
            # Retrieve or create the experience for the current user
            experience, created = Experience.objects.get_or_create(user=request.user)
            # Update the experience with the submitted data
            experience.title = experience_form.cleaned_data['title']
            experience.company = experience_form.cleaned_data['company']
            experience.start_date = experience_form.cleaned_data['start_date']
            experience.end_date = experience_form.cleaned_data['end_date']
            experience.description = experience_form.cleaned_data['description']
            experience.save()
            return redirect('user_profile', username)  # Replace with your success URL
    else:
        # Retrieve previous experience for the user (if exists)
        previous_experience = Experience.objects.filter(user=request.user).first()
        # Initialize the form with previous data if available, otherwise use empty form
        experience_form = ExperienceForm(instance=previous_experience)
    return render(request, 'add_experience.html', {'experience_form': experience_form})


from django.forms import formset_factory

def add_skill(request, username):
    if request.method == 'POST':
        skill_form = SkillsForm(request.POST)
        if skill_form.is_valid():
            skill, created = Skill.objects.get_or_create(user=request.user)
            skill.skills = skill_form.cleaned_data['skills']
            skill.save()
            return redirect('user_profile', username)
    else:
        previous_skill = Skill.objects.filter(user=request.user).first()
        skill_form = SkillsForm(instance=previous_skill)
    return render(request, 'add_skill.html', {'skill_form': skill_form})


def add_contact(request, username):
    if request.method == 'POST':
        contact_form = ContactInfoForm(request.POST)
        if contact_form.is_valid():
            # Retrieve or create the contact info for the current user
            contact, created = ContactInfo.objects.get_or_create(user=request.user)
            # Update the contact info with the submitted data
            contact.address = contact_form.cleaned_data['address']
            contact.phone_number = contact_form.cleaned_data['phone_number']
            contact.email = contact_form.cleaned_data['email']
            contact.save()
            return redirect('user_profile', username)  # Replace with your success URL
    else:
        # Retrieve previous contact info for the user (if exists)
        previous_contact = ContactInfo.objects.filter(user=request.user).first()
        # Initialize the form with previous data if available, otherwise use empty form
        contact_form = ContactInfoForm(instance=previous_contact)
    return render(request, 'add_contact.html', {'contact_form': contact_form})

# In views.py
from django.core.exceptions import ObjectDoesNotExist

@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts_url = request.path == f'/profile/{user.username}/'
    about_url = request.path == f'/profile/{user.username}/about/'
    classes_url = request.path == f'/profile/{user.username}/classes/'
    classes = None
    educations = None
    experiences = None
    skills = None
    contact_info = None

    try:
        contact_info = ContactInfo.objects.get(user=user)
    except ObjectDoesNotExist:
        pass

    if request.user.role == 'STUDENT':
        try:
            educations = Education.objects.filter(user=user)
        except ObjectDoesNotExist:
            pass
        try:
            experiences = Experience.objects.filter(user=user)
        except ObjectDoesNotExist:
            pass
        try:
            skills = Skill.objects.filter(user=user)
        except ObjectDoesNotExist:
            pass



    if request.method == 'POST':
        send_form = SendMessageForm(request.POST)
        if send_form.is_valid():
            message = send_form.save(commit=False)
            message.sender = request.user
            message.receiver = user  # Set the receiver to the profile user
            message.save()
            return redirect('home')
    else:
        # Set the initial receiver value to the profile user
        send_form = SendMessageForm(initial={'receiver': user})


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
        if class_form.is_valid():
            new_class = form.save(commit=False)
            new_class.teacher = request.user.teacher
            new_class.save()
            return redirect('user_profile', username=request.user.username)
    else:
        class_form = ClassForm()

    if user.role == 'TEACHER':
        try:
            classes = Class.objects.filter(teacher=user.teacher).prefetch_related('students')
        except ObjectDoesNotExist:
            pass
    elif user.role == 'STUDENT':
        try:
            classes = Class.objects.filter(students=user.student).prefetch_related('students')
        except ObjectDoesNotExist:
            pass
    follow_request_sent = Notification.objects.filter(sender=request.user, receiver=user, type='follow_request').exists()

    context = {
        'classes_url': classes_url,
        'classes': classes,
        'class_form': class_form,
        'user': user,
        'form': form,
        'posts': posts,
        'shared_posts': shared_posts,
        'posts_url': posts_url,
        'about_url': about_url,
        'follow_request_sent': follow_request_sent,
        'educations': educations,
        'experiences': experiences,
        'skills': skills,
        'contact_info': contact_info,
        'send_form' : send_form
    }

    return render(request, 'user_profile.html', context)


def create_offer(request, username):
    if request.method == 'POST':
        offer_form = CreateOffer(request.POST)
        if offer_form.is_valid():
            new_offer = offer_form.save(commit=False)
            new_offer.creator = request.user
            new_offer.save()
            return redirect('user_profile', username=username)
    else:
        offer_form = CreateOffer()  # Create an empty form for GET requests

    return render(request, 'create_offer.html', {'offer_form': offer_form})

@login_required
def display_offers(request):
    filter_option = request.GET.get('filter')
    
    if filter_option == 'mine' and request.user.role == 'ENTERPRISE':
        offers = Offer.objects.filter(creator=request.user)
    else:
        offers = Offer.objects.all()

    return render(request, 'display_offers.html', {'offers': offers})

def apply_for_offer(request, offer_id):
    offer = Offer.objects.get(pk=offer_id)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.offer = offer
            application.applicant = request.user
            application.save()
            return redirect('display_offers')  # Redirect to a success page or offer details page
    else:
        form = ApplicationForm()
    return render(request, 'application_form.html', {'form': form, 'offer': offer})

def applications_list(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id)
    applications = offer.applications.all()
    return render(request, 'applications_list.html', {'offer': offer, 'applications': applications})


def create_class(request):

    if request.method == 'POST':
        class_form = ClassForm(request.POST)
        if class_form.is_valid():
            new_class = class_form.save(commit=False)
            new_class.teacher = request.user.teacher
            new_class.save()
            class_form.save_m2m() 
            return redirect('user_profile', username=request.user.username)
    else:
        class_form = ClassForm() 
    return render(request, 'create_class.html', {'class_form': class_form})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Class, Announcement
from .forms import AnnouncementForm

from django.contrib.auth.decorators import login_required
from django.http import Http404

@login_required
def class_detail(request, class_id, class_title):
    class_instance = get_object_or_404(Class, pk=class_id)


    # if not (request.user.role == User.Role.STUDENT or request.user.role == User.Role.TEACHER):
    #     raise Http404("You are not authorized to view this page.")

    if class_instance.teacher.user == request.user:
        is_authorized = True
    # Check if the user is one of the students enrolled in the class
    elif request.user.role == User.Role.STUDENT and class_instance.students.filter(user=request.user).exists():
        is_authorized = True
    else:
        is_authorized = False

    if not is_authorized:
       return render(request, '404.html')
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
    exams = Exam.objects.filter(class_instance=class_instance)
    context = {
        'class_instance': class_instance,
        'class_form': class_form,
        'assignment_form': assignment_form,
        'announcements': announcements,
        'assignments': assignments,
        'exams' : exams
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
    return redirect('assignment_detail', class_id=class_id, class_title=class_title, assignment_id=assignment_id)

from .models import Exam, Question, Answer

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Class, Exam
from .forms import ExamForm, QuestionForm, AnswerForm
from .models import Class, Exam, Question, Answer

from .models import Exam

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Exam, Question, StudentAnswer
from .forms import StudentAnswerForm

def take_exam(request, class_id,class_title ,exam_id):

    exam = Exam.objects.get(pk=exam_id)
    questions = Question.objects.filter(exam=exam)
    return render(request, 'take_exam.html', {'exam': exam, 'questions': questions})


def submit_exam(request, exam_id):
    if request.method == 'POST':
        for question_id, answer_id in request.POST.items():
            if question_id.startswith('answer_'):
                question_id = question_id.split('_')[1]
                correct_answer = Answer.objects.get(question_id=question_id, is_correct=True)
                student_answer_text = Answer.objects.get(id=answer_id).answer_text
                is_correct = (student_answer_text == correct_answer.answer_text)
                student_answer = StudentAnswer.objects.create(
                    student=request.user,
                    question_id=question_id,
                    answer_text=student_answer_text,
                    is_correct=is_correct
                )
                if is_correct:
                    student_answer.correct_answers_count += 1
                    student_answer.save()
        # Redirect to exam results page after submitting the exam
        return redirect('exam_results')
    else:
        # Handle GET request if needed.
        pass



def calculate_correct_answers(student):
    # Get all the student's answers
    student_answers = StudentAnswer.objects.filter(student=student)
    
    # Initialize a variable to count the correct answers
    correct_answers_count = 0
    
    # Loop through each student's answer
    for student_answer in student_answers:
        # Get the corresponding correct answer for the question
        correct_answer = Answer.objects.get(question=student_answer.question, is_correct=True)
        
        # Compare the student's answer with the correct answer
        if student_answer.answer_text == correct_answer.answer_text:
            correct_answers_count += 1
    
    return correct_answers_count




@login_required
def view_exam_results(request):
    student = request.user
    total_correct_answers = calculate_correct_answers(student)
    return render(request, 'exam_results.html', {'total_correct_answers': total_correct_answers})


def create_exam(request, class_id, class_title):
    class_instance = get_object_or_404(Class, pk=class_id)

    if request.method == 'POST':
        exam_form = ExamForm(request.POST)
        question_forms = [QuestionForm(request.POST, prefix=str(i)) for i in range(20)]
        answer_forms = [[AnswerForm(request.POST, prefix=f'answer-{i}-{j}') for j in range(3)] for i in range(20)]

        if exam_form.is_valid() and all(q.is_valid() for q in question_forms) and all(all(a.is_valid() for a in ans) for ans in answer_forms):
            exam = exam_form.save(commit=False)
            exam.class_instance = class_instance
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
        question_forms = [QuestionForm(prefix=str(i)) for i in range(20)]
        answer_forms = [[AnswerForm(prefix=f'answer-{i}-{j}') for j in range(3)] for i in range(20)]

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
    
    # Filter out users with no conversations with the current user
    users = users.filter(latest_message_id__isnull=False)
    
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
    receiver = get_object_or_404(User, pk=receiver_id)  
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

    return render(request, 'conversation_detail.html', {'messages': messages, 'receiver': receiver, 'form': form, 'sender' : sender})


def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        receiver = get_object_or_404(User, pk=receiver_id)
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.receiver = receiver
            new_message.save()
            messages.success(request, 'Message sent successfully.')
        else:
            messages.error(request, 'Failed to send message. Please try again.')
    return redirect('home') 













from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import ChangePasswordForm  # Import your custom form
from .models import Education, ContactInfo

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import (ChangeStudentInfoForm, ChangeTeacherInfoForm, 
                    ChangeEducationForm, ChangePasswordForm, 
                    ContactInfoForm, ExperienceForm, SkillsForm, )
from .models import Education, ContactInfo, Experience, Skill

from django.contrib.auth.forms import PasswordChangeForm




def update_info(request, username):
    user = request.user

    # Retrieve existing instances of user information
    skill_instance = Skill.objects.filter(user=user).first()
    education_instance = Education.objects.filter(user=user).first()
    experience_instance = Experience.objects.filter(user=user).first()
    contact_instance = ContactInfo.objects.filter(user=user).first()

    # Define form variables
    user_instance = user  # No need to query, as the user instance is readily available
    user_form = UserForm(instance=user_instance)
    skill_form = SkillsForm(prefix='skill', instance=skill_instance)
    education_form = EducationForm(prefix='education', instance=education_instance)
    experience_form = ExperienceForm(prefix='experience', instance=experience_instance)
    contact_form = ContactInfoForm(prefix='contact', instance=contact_instance)
    password_form = PasswordChangeForm(user=user_instance)

    if request.method == 'POST':
        if 'submit_user' in request.POST:
            user_form = UserForm(request.POST, instance=user_instance)
            if user_form.is_valid():
                user_form.save()
                return redirect('user_profile', username)
        elif 'submit_skill' in request.POST:
            skill_form = SkillsForm(request.POST, prefix='skill', instance=skill_instance)
            if skill_form.is_valid():
                skill = skill_form.save(commit=False)
                skill.user = user
                skill.save()
                return redirect('user_profile', username)
        elif 'submit_education' in request.POST:
            education_form = EducationForm(request.POST, prefix='education', instance=education_instance)
            if education_form.is_valid():
                education = education_form.save(commit=False)
                education.user = user
                education.save()
                return redirect('user_profile', username)
        elif 'submit_experience' in request.POST:
            experience_form = ExperienceForm(request.POST, prefix='experience', instance=experience_instance)
            if experience_form.is_valid():
                experience = experience_form.save(commit=False)
                experience.user = user
                experience.save()
                return redirect('user_profile', username)
        elif 'submit_contact' in request.POST:
            contact_form = ContactInfoForm(request.POST, prefix='contact', instance=contact_instance)
            if contact_form.is_valid():
                contact = contact_form.save(commit=False)
                contact.user = user
                contact.save()
                return redirect('user_profile', username)
        elif 'submit_password' in request.POST:
                    password_form = PasswordChangeForm(user=user_instance, data=request.POST)
                    if password_form.is_valid():
                        password_form.save()
                        update_session_auth_hash(request, password_form.user)
                        return redirect('user_profile', username)

    return render(request, 'update_info.html', {
        'user_form': user_form,
        'skill_form': skill_form,
        'education_form': education_form,
        'experience_form': experience_form,
        'contact_form': contact_form,
        'password_form': password_form,

    })


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
                # Save the user form first to ensure the instance is updated
                user_form.save()
                teacher_form.save()
                return redirect('user_profile', username=username)
    else:
        if user.role == 'STUDENT':
            user_form = ChangeStudentInfoForm(instance=user, initial={'profile_pic': user.profile_pic, 'profile_cover': user.profile_cover})
            student_form = StudentInfoForm(instance=user.student)
            context = {'user_form': user_form, 'student_form': student_form, 'posts_url': posts_url, 'about_url': about_url}
            return render(request, 'about_profile.html', context)
        elif user.role == 'TEACHER':
            user_form = ChangeTeacherInfoForm(instance=user, initial={'profile_pic': user.profile_pic, 'profile_cover': user.profile_cover})
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
    follow_request_sent = Notification.objects.filter(sender=request.user, receiver=user_to_follow, type='follow_request').exists()
    if not follow_request_sent:
        Notification.objects.create(
            sender=request.user,
            receiver=user_to_follow,
            message=f'{request.user.username} wants to follow you.',
            type='follow_request'
        )
    else:
        # If follow request already sent, remove it
        Notification.objects.filter(sender=request.user, receiver=user_to_follow, type='follow_request').delete()
    return redirect('user_profile', username=username)

def remove_follow_request(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    Notification.objects.filter(sender=request.user, receiver=user_to_unfollow, type='follow_request').delete()
    return redirect('user_profile', username=username)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()


def accept_follow_request(request, username):
    user_to_accept = get_object_or_404(User, username=username)
    
    request.user.followers.add(user_to_accept)
    
    user_to_accept.following.add(request.user)
    
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


@login_required
def like_post(request):
    post_id = request.POST.get('id')
    post = Post.objects.get(id=post_id)
    user = request.user
    liked = False
    if user in post.likes.all():
        post.likes.remove(user)
    else:
        post.likes.add(user)
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': post.likes.count()})
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

