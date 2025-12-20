"""
API URL configuration for LMS app.
All API endpoints are defined here.
"""

from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()

# Register all ViewSets with the router
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'students', views.StudentViewSet, basename='student')
router.register(r'teachers', views.TeacherViewSet, basename='teacher')
router.register(r'parents', views.ParentViewSet, basename='parent')
router.register(r'academic-years', views.AcademicYearViewSet, basename='academic-year')
router.register(r'classes', views.ClassViewSet, basename='class')
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'class-subjects', views.ClassSubjectViewSet, basename='class-subject')
router.register(r'timetables', views.TimetableViewSet, basename='timetable')
router.register(r'content', views.ContentViewSet, basename='content')
router.register(r'assessments', views.AssessmentViewSet, basename='assessment')
router.register(r'questions', views.QuestionViewSet, basename='question')
router.register(r'submissions', views.SubmissionViewSet, basename='submission')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')
router.register(r'fee-structures', views.FeeStructureViewSet, basename='fee-structure')
router.register(r'fee-payments', views.FeePaymentViewSet, basename='fee-payment')
router.register(r'announcements', views.AnnouncementViewSet, basename='announcement')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'reports', views.ReportViewSet, basename='report')

# URL patterns for the API
urlpatterns = [
    # All ViewSet endpoints (users/, students/, teachers/, etc.)
    path('', include(router.urls)),
    
    # Custom authentication endpoint
    path('login/', views.login_view, name='api_login'),
    
    # Dashboard endpoints for different roles
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/parent/', views.parent_dashboard, name='parent_dashboard'),
    
    # Health check endpoint (required for Railway deployment)
    path('health/', lambda request: JsonResponse({'status': 'healthy', 'service': 'school-management-api'}), name='health_check'),
]