from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('resume/upload/', views.resume_upload, name='resume_upload'),
    path('resume/<int:resume_id>/', views.resume_detail, name='resume_detail'),
    path('resume/<int:resume_id>/version/', views.create_version, name='create_version'),
    path('job/create/', views.job_create, name='job_create'),
    path('analysis/<int:resume_id>/<int:job_id>/', views.run_analysis, name='run_analysis'),
    path('analysis/detail/<int:analysis_id>/', views.analysis_detail, name='analysis_detail'),
    path('analysis/<int:analysis_id>/report/', views.download_report, name='download_report'),
    path('analysis/<int:analysis_id>/rewrite/', views.rewrite_view, name='rewrite'),
]
