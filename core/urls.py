from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import job_applier_dashboard,job_dashboard,parse_resume_api

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('plans/', views.plans, name='plans'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('profile-form/', views.profile_form, name='profile_form'),
    path('job_applier_dashboard/', job_applier_dashboard, name='job_applier_dashboard'),
    path('applyJob/', views.applied_job_create, name='applied-job-create'),
    path('filteredJobs/', views.get_filtered_jobs, name='filtered_jobs'),
    path('dashboard/', job_dashboard, name='job_dashboard'),
    path("api/parse-resume/", parse_resume_api, name="parse-resume-api"),


]