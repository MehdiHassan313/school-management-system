from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('principal', 'Principal'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


class Student(models.Model):
    """
    Student profile model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    enrollment_date = models.DateField()
    grade = models.CharField(max_length=10)  # e.g., 'Grade 1', 'Grade 2'
    section = models.CharField(max_length=5)  # e.g., 'A', 'B'
    parent = models.ForeignKey('Parent', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.grade} {self.section}"


class Teacher(models.Model):
    """
    Teacher profile model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    teacher_id = models.CharField(max_length=20, unique=True)
    hire_date = models.DateField()
    subjects = models.ManyToManyField('Subject', related_name='teachers')
    qualifications = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Parent(models.Model):
    """
    Parent profile model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    parent_id = models.CharField(max_length=20, unique=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    relationship_to_student = models.CharField(max_length=50, choices=[
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
    ], default='father')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class AcademicYear(models.Model):
    """
    Academic year model
    """
    name = models.CharField(max_length=20, unique=True)  # e.g., '2023-2024'
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Class(models.Model):
    """
    Class model (grade and section)
    """
    grade = models.CharField(max_length=10)  # e.g., 'Grade 1'
    section = models.CharField(max_length=5)  # e.g., 'A'
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ['grade', 'section', 'academic_year']

    def __str__(self):
        return f"{self.grade} {self.section} ({self.academic_year.name})"


class Subject(models.Model):
    """
    Subject model
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    grade = models.CharField(max_length=10)  # Associated grade

    def __str__(self):
        return f"{self.name} ({self.grade})"


class ClassSubject(models.Model):
    """
    Many-to-many relationship between Class and Subject with teacher assignment
    """
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['class_obj', 'subject']

    def __str__(self):
        return f"{self.class_obj} - {self.subject} - {self.teacher}"


class Timetable(models.Model):
    """
    Class timetable model
    """
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]

    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    period = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ['class_obj', 'day', 'period']

    def __str__(self):
        return f"{self.class_obj} - {self.day} - Period {self.period}"


class Content(models.Model):
    """
    Learning content model
    """
    CONTENT_TYPES = [
        ('pdf', 'PDF'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('ppt', 'PowerPoint'),
        ('doc', 'Word Document'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    file = models.FileField(upload_to='content/')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.CharField(max_length=10)
    chapter = models.CharField(max_length=100, blank=True, null=True)
    uploaded_by = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_homework = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Assessment(models.Model):
    """
    Assessment/Quiz model
    """
    ASSESSMENT_TYPES = [
        ('quiz', 'Quiz'),
        ('exam', 'Exam'),
        ('assignment', 'Assignment'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    total_marks = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.class_obj}"


class Question(models.Model):
    """
    Question model for assessments
    """
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    marks = models.IntegerField()

    # For MCQ
    option_a = models.CharField(max_length=200, blank=True, null=True)
    option_b = models.CharField(max_length=200, blank=True, null=True)
    option_c = models.CharField(max_length=200, blank=True, null=True)
    option_d = models.CharField(max_length=200, blank=True, null=True)
    correct_answer = models.CharField(max_length=1, choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')], blank=True, null=True)

    def __str__(self):
        return f"Q: {self.question_text[:50]}..."


class Submission(models.Model):
    """
    Student submission for assessments
    """
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.IntegerField(blank=True, null=True)
    grade = models.CharField(max_length=2, blank=True, null=True)  # A, B, C, etc.
    feedback = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['assessment', 'student']

    def __str__(self):
        return f"{self.student} - {self.assessment}"


class Attendance(models.Model):
    """
    Attendance model
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ], default='present')
    marked_by = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['student', 'date']

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"


class FeeStructure(models.Model):
    """
    Fee structure model
    """
    FEE_TYPES = [
        ('tuition', 'Tuition Fee'),
        ('exam', 'Exam Fee'),
        ('transport', 'Transport Fee'),
        ('misc', 'Miscellaneous'),
    ]

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPES)
    grade = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.fee_type} - {self.grade} - {self.academic_year}"


class FeePayment(models.Model):
    """
    Fee payment tracking
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('online', 'Online'),
        ('cheque', 'Cheque'),
    ])
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.fee_structure} - {self.amount_paid}"


class Announcement(models.Model):
    """
    School announcements
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    target_audience = models.CharField(max_length=20, choices=[
        ('all', 'All Users'),
        ('teachers', 'Teachers'),
        ('students', 'Students'),
        ('parents', 'Parents'),
    ], default='all')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    """
    Private messaging between users
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.subject}"


class Notification(models.Model):
    """
    Notification system
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=[
        ('announcement', 'Announcement'),
        ('attendance', 'Attendance'),
        ('fee', 'Fee Reminder'),
        ('assessment', 'Assessment'),
        ('message', 'Message'),
    ])
    created_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    sent_via_email = models.BooleanField(default=False)
    sent_via_sms = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}: {self.title}"


class Report(models.Model):
    """
    General reports model
    """
    REPORT_TYPES = [
        ('academic', 'Academic Performance'),
        ('attendance', 'Attendance Report'),
        ('fee', 'Fee Collection Report'),
        ('class', 'Class Report'),
    ]

    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='reports/')
    parameters = models.JSONField(blank=True, null=True)  # Store filter parameters

    def __str__(self):
        return f"{self.report_type} - {self.title}"
