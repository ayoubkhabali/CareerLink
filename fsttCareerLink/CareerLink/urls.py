from django.urls import path
from .views import home
from . import views
from django.http import HttpResponse
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView
urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.welcome, name='welcome'),
    path('about_us', views.aboutUs, name='about'),
    path('logout/',views.logoutUser,name="logout"),
    path('login/',views.loginPage,name="login"),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.comment_post, name='comment_post'),
    path('share/<int:post_id>/', views.share_post, name='share_post'),
    path('profile/about/', views.profile, name='profile-edit'),
    path('profile/<str:username>', RedirectView.as_view(url='/profile/%(username)s/')),
    path('profile/<str:username>/about/', views.user_profile, name='about_profile'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('profile/<str:username>/update/', views.update_profile, name='update_profile'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/classes/', views.user_profile, name='classes'),
    path('profile/<str:username>/classes', RedirectView.as_view(url='/profile/%(username)s/classes/')),
    path('classes/create-class', views.create_class,name="create_class"),
    # path('class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('class/<int:class_id>/<str:class_title>/', views.class_detail, name='class_detail'),
    path('class/<int:class_id>/<str:class_title>/assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('class/<int:class_id>/<str:class_title>/assignment/<int:assignment_id>/unsubmit/', views.unsubmit_assignment, name='unsubmit_assignment'),
    path('class/<int:class_id>/<str:class_title>/create-exam', views.create_exam, name='create_exam'),
    path('exam/<int:class_id>/<str:class_title>/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:receiver_id>/', views.conversation_detail, name='conversation_detail'),
    path('search-users/', views.search_users, name='search_users'),
    path('search-students/', views.search_students, name='search_students'),
    path('profile/<str:username>/add-education/', views.add_education, name='add_education'),
    path('profile/<str:username>/add-interest-skill/', views.add_interest_skill, name='add_interest_skill'),
    path('profile/<str:username>/add-contact/', views.add_contact, name='add_contact'),
    path('profile/<str:username>/add-experience/', views.add_experience, name='add_experience'),
    path('notifications/<str:username>/accept/', views.accept_follow_request, name='accept_follow_request'),
    path('notifications/<str:username>/decline/', views.refuse_follow_request, name='refuse_follow_request'),
    path('remove_follow_request/<str:username>/', views.remove_follow_request, name='remove_follow_request'),

   
]


from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
