from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Student, Teacher, Parent, AcademicYear, Class, Subject,
    ClassSubject, Timetable, Content, Assessment, Question, Submission,
    Attendance, FeeStructure, FeePayment, Announcement, Message, Notification, Report
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'address', 'date_of_birth', 'profile_picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'address', 'date_of_birth', 'profile_picture')}),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'grade', 'section', 'enrollment_date', 'parent')
    list_filter = ('grade', 'section', 'enrollment_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'student_id')
    ordering = ('grade', 'section', 'user__last_name')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'teacher_id', 'hire_date', 'qualifications')
    list_filter = ('hire_date',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'teacher_id')
    ordering = ('user__last_name',)


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'parent_id', 'relationship_to_student', 'occupation')
    list_filter = ('relationship_to_student',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'parent_id')
    ordering = ('user__last_name',)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('grade', 'section', 'academic_year', 'class_teacher')
    list_filter = ('grade', 'section', 'academic_year')
    search_fields = ('grade', 'section', 'class_teacher__user__first_name', 'class_teacher__user__last_name')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'grade')
    list_filter = ('grade',)
    search_fields = ('name', 'code')


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ('class_obj', 'subject', 'teacher')
    list_filter = ('class_obj__grade', 'subject__name')
    search_fields = ('class_obj__grade', 'subject__name', 'teacher__user__first_name')


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('class_obj', 'day', 'period', 'subject', 'start_time', 'end_time')
    list_filter = ('day', 'class_obj__grade')
    search_fields = ('class_obj__grade', 'subject__name')


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'subject', 'grade', 'uploaded_by', 'upload_date')
    list_filter = ('content_type', 'grade', 'upload_date')
    search_fields = ('title', 'subject__name', 'uploaded_by__user__first_name')


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'assessment_type', 'subject', 'class_obj', 'scheduled_date', 'teacher')
    list_filter = ('assessment_type', 'scheduled_date', 'class_obj__grade')
    search_fields = ('title', 'subject__name', 'teacher__user__first_name')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'question_type', 'marks')
    list_filter = ('question_type',)
    search_fields = ('assessment__title',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assessment', 'submitted_at', 'marks_obtained', 'grade')
    list_filter = ('submitted_at', 'grade')
    search_fields = ('student__user__first_name', 'assessment__title')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'marked_by', 'class_obj')
    list_filter = ('status', 'date', 'class_obj__grade')
    search_fields = ('student__user__first_name', 'marked_by__user__first_name')


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('fee_type', 'grade', 'academic_year', 'amount', 'due_date')
    list_filter = ('fee_type', 'grade', 'academic_year')
    search_fields = ('fee_type', 'grade')


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'amount_paid', 'payment_date', 'is_paid')
    list_filter = ('is_paid', 'payment_date', 'fee_structure__fee_type')
    search_fields = ('student__user__first_name', 'fee_structure__fee_type')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_date', 'target_audience', 'is_active')
    list_filter = ('target_audience', 'is_active', 'created_date')
    search_fields = ('title', 'created_by__username')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'subject', 'sent_date', 'is_read')
    list_filter = ('sent_date', 'is_read')
    search_fields = ('sender__username', 'receiver__username', 'subject')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'created_date', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_date')
    search_fields = ('user__username', 'title')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'generated_by', 'generated_date')
    list_filter = ('report_type', 'generated_date')
    search_fields = ('title', 'generated_by__username')
