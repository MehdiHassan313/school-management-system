"""
Views for School Management System
API ViewSets and Template views
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

# Import your custom User model (NOT django.contrib.auth.models.User)
from .models import (
    User, Student, Teacher, Parent, AcademicYear, Class, Subject,
    ClassSubject, Timetable, Content, Assessment, Question, Submission,
    Attendance, FeeStructure, FeePayment, Announcement, Message, Notification, Report
)

# Import ALL serializers
from .serializers import (
    UserSerializer, LoginSerializer, StudentSerializer, TeacherSerializer, ParentSerializer,
    AcademicYearSerializer, ClassSerializer, SubjectSerializer, ClassSubjectSerializer,
    TimetableSerializer, ContentSerializer, AssessmentSerializer, QuestionSerializer,
    SubmissionSerializer, AttendanceSerializer, FeeStructureSerializer, FeePaymentSerializer,
    AnnouncementSerializer, MessageSerializer, NotificationSerializer, ReportSerializer
)

# ==================== HELPER FUNCTION ====================
def calculate_attendance_percentage(student):
    """
    Helper function to calculate attendance percentage
    """
    total_days = Attendance.objects.filter(student=student).count()
    if total_days == 0:
        return 0
    present_days = Attendance.objects.filter(student=student, status='present').count()
    return round((present_days / total_days) * 100, 2)


# ==================== API VIEWSETS ====================

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'register']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login view for JWT authentication
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Student management
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Student.objects.filter(user=user)
        elif user.role == 'parent':
            try:
                parent = Parent.objects.get(user=user)
                return Student.objects.filter(parent=parent)
            except Parent.DoesNotExist:
                return Student.objects.none()
        return super().get_queryset()


class TeacherViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Teacher management
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return Teacher.objects.filter(user=user)
        return super().get_queryset()


class ParentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Parent management
    """
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'parent':
            return Parent.objects.filter(user=user)
        return super().get_queryset()


class AcademicYearViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Academic Year management
    """
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAuthenticated]


class ClassViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Class management
    """
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]


class SubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Subject management
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


class ClassSubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Class-Subject-Teacher assignments
    """
    queryset = ClassSubject.objects.all()
    serializer_class = ClassSubjectSerializer
    permission_classes = [IsAuthenticated]


class TimetableViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Timetable management
    """
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Timetable.objects.filter(class_obj__grade=student.grade, class_obj__section=student.section)
            except Student.DoesNotExist:
                return Timetable.objects.none()
        elif user.role == 'teacher':
            try:
                teacher = Teacher.objects.get(user=user)
                return Timetable.objects.filter(subject__in=teacher.subjects.all())
            except Teacher.DoesNotExist:
                return Timetable.objects.none()
        return super().get_queryset()


class ContentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Content management
    """
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Content.objects.filter(grade=student.grade)
            except Student.DoesNotExist:
                return Content.objects.none()
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'teacher':
            teacher = Teacher.objects.get(user=user)
            serializer.save(uploaded_by=teacher)


class AssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Assessment management
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Assessment.objects.filter(class_obj__grade=student.grade, class_obj__section=student.section)
            except Student.DoesNotExist:
                return Assessment.objects.none()
        elif user.role == 'teacher':
            try:
                teacher = Teacher.objects.get(user=user)
                return Assessment.objects.filter(teacher=teacher)
            except Teacher.DoesNotExist:
                return Assessment.objects.none()
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'teacher':
            teacher = Teacher.objects.get(user=user)
            serializer.save(teacher=teacher)


class QuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Question management
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Submission management
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Submission.objects.filter(student=student)
            except Student.DoesNotExist:
                return Submission.objects.none()
        elif user.role == 'teacher':
            try:
                teacher = Teacher.objects.get(user=user)
                return Submission.objects.filter(assessment__teacher=teacher)
            except Teacher.DoesNotExist:
                return Submission.objects.none()
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'student':
            student = Student.objects.get(user=user)
            serializer.save(student=student)


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Attendance management
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return Attendance.objects.filter(student=student)
            except Student.DoesNotExist:
                return Attendance.objects.none()
        elif user.role == 'teacher':
            try:
                teacher = Teacher.objects.get(user=user)
                return Attendance.objects.filter(marked_by=teacher)
            except Teacher.DoesNotExist:
                return Attendance.objects.none()
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'teacher':
            teacher = Teacher.objects.get(user=user)
            serializer.save(marked_by=teacher)


class FeeStructureViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Fee Structure management
    """
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAuthenticated]


class FeePaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Fee Payment management
    """
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                return FeePayment.objects.filter(student=student)
            except Student.DoesNotExist:
                return FeePayment.objects.none()
        elif user.role == 'parent':
            try:
                parent = Parent.objects.get(user=user)
                return FeePayment.objects.filter(student__parent=parent)
            except Parent.DoesNotExist:
                return FeePayment.objects.none()
        return super().get_queryset()


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Announcement management
    """
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Announcement.objects.filter(is_active=True)
        if user.role != 'admin':
            queryset = queryset.filter(
                Q(target_audience='all') | Q(target_audience=user.role + 's')
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message management
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(receiver=user))

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Notification management
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user)


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Report management
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)


# ==================== DASHBOARD API VIEWS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    """
    Admin dashboard with overview statistics
    """
    data = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_parents': Parent.objects.count(),
        'total_classes': Class.objects.count(),
        'total_subjects': Subject.objects.count(),
        'active_academic_year': AcademicYearSerializer(
            AcademicYear.objects.filter(is_active=True).first()
        ).data if AcademicYear.objects.filter(is_active=True).exists() else None,
        'recent_announcements': AnnouncementSerializer(
            Announcement.objects.filter(is_active=True)[:5], many=True
        ).data,
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_dashboard(request):
    """
    Teacher dashboard
    """
    user = request.user
    try:
        teacher = Teacher.objects.get(user=user)
        data = {
            'teacher_info': TeacherSerializer(teacher).data,
            'assigned_subjects': SubjectSerializer(teacher.subjects.all(), many=True).data,
            'upcoming_assessments': AssessmentSerializer(
                Assessment.objects.filter(teacher=teacher, scheduled_date__gte=timezone.now())[:5], many=True
            ).data,
            'recent_content': ContentSerializer(
                Content.objects.filter(uploaded_by=teacher)[:5], many=True
            ).data,
        }
        return Response(data)
    except Teacher.DoesNotExist:
        return Response({'error': 'Teacher profile not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    """
    Student dashboard
    """
    user = request.user
    try:
        student = Student.objects.get(user=user)
        data = {
            'student_info': StudentSerializer(student).data,
            'timetable': TimetableSerializer(
                Timetable.objects.filter(class_obj__grade=student.grade, class_obj__section=student.section), many=True
            ).data,
            'upcoming_assessments': AssessmentSerializer(
                Assessment.objects.filter(
                    class_obj__grade=student.grade,
                    class_obj__section=student.section,
                    scheduled_date__gte=timezone.now()
                )[:5], many=True
            ).data,
            'recent_content': ContentSerializer(
                Content.objects.filter(grade=student.grade)[:5], many=True
            ).data,
            'attendance_percentage': calculate_attendance_percentage(student),
        }
        return Response(data)
    except Student.DoesNotExist:
        return Response({'error': 'Student profile not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def parent_dashboard(request):
    """
    Parent dashboard
    """
    user = request.user
    try:
        parent = Parent.objects.get(user=user)
        children = Student.objects.filter(parent=parent)
        data = {
            'parent_info': ParentSerializer(parent).data,
            'children': StudentSerializer(children, many=True).data,
            'children_attendance': [
                {
                    'student': StudentSerializer(child).data,
                    'attendance_percentage': calculate_attendance_percentage(child)
                } for child in children
            ],
            'unpaid_fees': FeePaymentSerializer(
                FeePayment.objects.filter(student__in=children, is_paid=False), many=True
            ).data,
        }
        return Response(data)
    except Parent.DoesNotExist:
        return Response({'error': 'Parent profile not found'}, status=404)


# ==================== TEMPLATE VIEWS ====================

def home(request):
    """
    Home page view
    """
    return render(request, 'home.html')


def user_login(request):
    """
    Login view for template-based authentication
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def user_register(request):
    """
    Register view for template-based authentication
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Simple registration
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='student'  # Default role
            )
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'register.html')


@login_required
def dashboard(request):
    """
    Dashboard view for authenticated users
    """
    user = request.user
    dashboard_data = {}

    if user.role == 'admin':
        dashboard_data = {
            'total_students': Student.objects.count(),
            'total_teachers': Teacher.objects.count(),
            'total_parents': Parent.objects.count(),
            'total_classes': Class.objects.count(),
        }
    elif user.role == 'teacher':
        try:
            teacher = Teacher.objects.get(user=user)
            dashboard_data = {
                'teacher_info': teacher,
                'assigned_subjects': teacher.subjects.all(),
                'upcoming_assessments': Assessment.objects.filter(teacher=teacher, scheduled_date__gte=timezone.now())[:5],
                'recent_content': Content.objects.filter(uploaded_by=teacher)[:5],
            }
        except Teacher.DoesNotExist:
            pass
    elif user.role == 'student':
        try:
            student = Student.objects.get(user=user)
            dashboard_data = {
                'student_info': student,
                'timetable': Timetable.objects.filter(class_obj__grade=student.grade, class_obj__section=student.section),
                'upcoming_assessments': Assessment.objects.filter(
                    class_obj__grade=student.grade,
                    class_obj__section=student.section,
                    scheduled_date__gte=timezone.now()
                )[:5],
                'recent_content': Content.objects.filter(grade=student.grade)[:5],
                'attendance_percentage': calculate_attendance_percentage(student),
            }
        except Student.DoesNotExist:
            pass
    elif user.role == 'parent':
        try:
            parent = Parent.objects.get(user=user)
            children = Student.objects.filter(parent=parent)
            dashboard_data = {
                'parent_info': parent,
                'children': children,
                'children_attendance': [
                    {
                        'student': child,
                        'attendance_percentage': calculate_attendance_percentage(child)
                    } for child in children
                ],
                'unpaid_fees': FeePayment.objects.filter(student__in=children, is_paid=False),
            }
        except Parent.DoesNotExist:
            pass

    return render(request, 'dashboard.html', {'dashboard_data': dashboard_data})


def user_logout(request):
    """
    Logout view
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')