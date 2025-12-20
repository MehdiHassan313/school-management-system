"""
Serializers for School Management System
"""

from rest_framework import serializers
from django.contrib.auth import authenticate

# Import ALL models
from .models import (
    User, Student, Teacher, Parent, AcademicYear, Class, Subject,
    ClassSubject, Timetable, Content, Assessment, Question, Submission,
    Attendance, FeeStructure, FeePayment, Announcement, Message, Notification, Report
)


# ==================== AUTHENTICATION SERIALIZERS ====================

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone_number', 'address', 'date_of_birth',
            'is_active', 'is_staff', 'date_joined', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'date_joined': {'read_only': True},
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login authentication
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError("User account is disabled.")
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        
        return data


# ==================== MODEL SERIALIZERS ====================

class StudentSerializer(serializers.ModelSerializer):
    """
    Serializer for Student model
    """
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['enrollment_date']


class TeacherSerializer(serializers.ModelSerializer):
    """
    Serializer for Teacher model
    """
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Teacher
        fields = '__all__'
        read_only_fields = ['hire_date']


class ParentSerializer(serializers.ModelSerializer):
    """
    Serializer for Parent model
    """
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Parent
        fields = '__all__'


class AcademicYearSerializer(serializers.ModelSerializer):
    """
    Serializer for AcademicYear model
    """
    class Meta:
        model = AcademicYear
        fields = '__all__'
        read_only_fields = ['created_at']


class ClassSerializer(serializers.ModelSerializer):
    """
    Serializer for Class model
    """
    class Meta:
        model = Class
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Subject model
    """
    class Meta:
        model = Subject
        fields = '__all__'


class ClassSubjectSerializer(serializers.ModelSerializer):
    """
    Serializer for ClassSubject model
    """
    class_details = ClassSerializer(source='class_obj', read_only=True)
    subject_details = SubjectSerializer(source='subject', read_only=True)
    teacher_details = TeacherSerializer(source='teacher', read_only=True)
    
    class Meta:
        model = ClassSubject
        fields = '__all__'


class TimetableSerializer(serializers.ModelSerializer):
    """
    Serializer for Timetable model
    """
    class_details = ClassSerializer(source='class_obj', read_only=True)
    subject_details = SubjectSerializer(source='subject', read_only=True)
    teacher_details = TeacherSerializer(source='teacher', read_only=True)
    
    class Meta:
        model = Timetable
        fields = '__all__'


class ContentSerializer(serializers.ModelSerializer):
    """
    Serializer for Content model
    """
    uploaded_by_details = TeacherSerializer(source='uploaded_by', read_only=True)
    
    class Meta:
        model = Content
        fields = '__all__'
        read_only_fields = ['upload_date']


class AssessmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Assessment model
    """
    teacher_details = TeacherSerializer(source='teacher', read_only=True)
    class_details = ClassSerializer(source='class_obj', read_only=True)
    subject_details = SubjectSerializer(source='subject', read_only=True)
    
    class Meta:
        model = Assessment
        fields = '__all__'
        read_only_fields = ['created_date']


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for Question model
    """
    class Meta:
        model = Question
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Submission model
    """
    student_details = StudentSerializer(source='student', read_only=True)
    assessment_details = AssessmentSerializer(source='assessment', read_only=True)
    
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['submitted_at']


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendance model
    """
    student_details = StudentSerializer(source='student', read_only=True)
    marked_by_details = TeacherSerializer(source='marked_by', read_only=True)
    class_details = ClassSerializer(source='class_obj', read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'


class FeeStructureSerializer(serializers.ModelSerializer):
    """
    Serializer for FeeStructure model
    """
    academic_year_details = AcademicYearSerializer(source='academic_year', read_only=True)
    
    class Meta:
        model = FeeStructure
        fields = '__all__'


class FeePaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for FeePayment model
    """
    student_details = StudentSerializer(source='student', read_only=True)
    fee_structure_details = FeeStructureSerializer(source='fee_structure', read_only=True)
    
    class Meta:
        model = FeePayment
        fields = '__all__'
        read_only_fields = ['payment_date']


class AnnouncementSerializer(serializers.ModelSerializer):
    """
    Serializer for Announcement model
    """
    created_by_details = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ['created_date']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    """
    sender_details = UserSerializer(source='sender', read_only=True)
    receiver_details = UserSerializer(source='receiver', read_only=True)
    
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['sent_date']


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model
    """
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_date']


class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Report model
    """
    generated_by_details = UserSerializer(source='generated_by', read_only=True)
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['generated_date']