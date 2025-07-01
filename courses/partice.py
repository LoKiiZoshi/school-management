# ================================
# PROJECT STRUCTURE
# ================================
"""
schoolmanagement/
├── schoolmanagement/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── students/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── teachers/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── courses/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── academics/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── fees/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── library/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── transport/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── manage.py
├── requirements.txt
└── db.sqlite3
"""

# ================================
# schoolmanagement/settings.py
# ================================
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-here-change-in-production'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'students',
    'teachers',
    'courses',
    'academics',
    'fees',
    'library',
    'transport',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'schoolmanagement.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'schoolmanagement.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

CORS_ALLOW_ALL_ORIGINS = True

# ================================
# schoolmanagement/urls.py
# ================================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/students/', include('students.urls')),
    path('api/teachers/', include('teachers.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/academics/', include('academics.urls')),
    path('api/fees/', include('fees.urls')),
    path('api/library/', include('library.urls')),
    path('api/transport/', include('transport.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ================================
# students/models.py
# ================================
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator

class Grade(models.Model):
    name = models.CharField(max_length=50, unique=True)
    level = models.IntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['level']

    def __str__(self):
        return self.name

class Section(models.Model):
    name = models.CharField(max_length=10)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='sections')
    capacity = models.IntegerField(default=30)
    room_number = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ['name', 'grade']

    def __str__(self):
        return f"{self.grade.name} - {self.name}"

class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=10)
    admission_number = models.CharField(max_length=20, unique=True)
    admission_date = models.DateField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=17)
    parent_name = models.CharField(max_length=100)
    parent_email = models.EmailField()
    parent_phone = models.CharField(validators=[phone_regex], max_length=17)
    profile_picture = models.ImageField(upload_to='students/profiles/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['roll_number', 'section']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"

class StudentAttendance(models.Model):
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
        ('E', 'Excused'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    remarks = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'date']

    def __str__(self):
        return f"{self.student} - {self.date} - {self.get_status_display()}"

# ================================
# students/serializers.py
# ================================
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Grade, Section, Student, StudentAttendance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class GradeSerializer(serializers.ModelSerializer):
    sections_count = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = '__all__'

    def get_sections_count(self, obj):
        return obj.sections.count()

class SectionSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = '__all__'

    def get_students_count(self, obj):
        return obj.student_set.count()

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'

    def get_age(self, obj):
        from datetime import date
        today = date.today()
        return today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))

class StudentCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Student
        exclude = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        user_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
        }
        user = User.objects.create_user(**user_data)
        student = Student.objects.create(user=user, **validated_data)
        return student

class StudentAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)

    class Meta:
        model = StudentAttendance
        fields = '__all__'

class BulkAttendanceSerializer(serializers.Serializer):
    date = serializers.DateField()
    attendances = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

    def create(self, validated_data):
        date = validated_data['date']
        attendances_data = validated_data['attendances']
        user = self.context['request'].user
        
        attendance_objects = []
        for attendance_data in attendances_data:
            student_id = attendance_data['student_id']
            status = attendance_data['status']
            remarks = attendance_data.get('remarks', '')
            
            try:
                student = Student.objects.get(student_id=student_id)
                attendance, created = StudentAttendance.objects.get_or_create(
                    student=student,
                    date=date,
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'recorded_by': user
                    }
                )
                if not created:
                    attendance.status = status
                    attendance.remarks = remarks
                    attendance.recorded_by = user
                    attendance.save()
                attendance_objects.append(attendance)
            except Student.DoesNotExist:
                continue
        
        return attendance_objects

# ================================
# students/views.py
# ================================
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from datetime import date, timedelta
from .models import Grade, Section, Student, StudentAttendance
from .serializers import (
    GradeSerializer, SectionSerializer, StudentSerializer, 
    StudentCreateSerializer, StudentAttendanceSerializer, BulkAttendanceSerializer
)

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['level', 'name', 'created_at']
    ordering = ['level']

    @action(detail=True, methods=['get'])
    def sections(self, request, pk=None):
        grade = self.get_object()
        sections = grade.sections.all()
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        grade = self.get_object()
        students = Student.objects.filter(grade=grade, is_active=True)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        stats = Grade.objects.annotate(
            sections_count=Count('sections'),
            students_count=Count('student', filter=Q(student__is_active=True))
        ).values('id', 'name', 'level', 'sections_count', 'students_count')
        return Response(stats)

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.select_related('grade').all()
    serializer_class = SectionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['grade', 'grade__level']
    search_fields = ['name', 'room_number']

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        section = self.get_object()
        students = Student.objects.filter(section=section, is_active=True)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        section = self.get_object()
        students = Student.objects.filter(section=section, is_active=True)
        
        summary = []
        for student in students:
            total_days = StudentAttendance.objects.filter(student=student).count()
            present_days = StudentAttendance.objects.filter(student=student, status='P').count()
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            summary.append({
                'student_id': student.student_id,
                'student_name': student.user.get_full_name(),
                'total_days': total_days,
                'present_days': present_days,
                'attendance_percentage': round(attendance_percentage, 2)
            })
        
        return Response(summary)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'grade', 'section').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['grade', 'section', 'gender', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'student_id', 'admission_number']
    ordering_fields = ['user__first_name', 'admission_date', 'created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return StudentCreateSerializer
        return StudentSerializer

    @action(detail=True, methods=['get'])
    def attendance_history(self, request, pk=None):
        student = self.get_object()
        attendances = StudentAttendance.objects.filter(student=student).order_by('-date')
        serializer = StudentAttendanceSerializer(attendances, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        student = self.get_object()
        
        # Current month
        today = date.today()
        first_day = today.replace(day=1)
        
        total_days = StudentAttendance.objects.filter(
            student=student, 
            date__gte=first_day
        ).count()
        
        present_days = StudentAttendance.objects.filter(
            student=student, 
            date__gte=first_day, 
            status='P'
        ).count()
        
        late_days = StudentAttendance.objects.filter(
            student=student, 
            date__gte=first_day, 
            status='L'
        ).count()
        
        absent_days = StudentAttendance.objects.filter(
            student=student, 
            date__gte=first_day, 
            status='A'
        ).count()
        
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        return Response({
            'student_id': student.student_id,
            'student_name': student.user.get_full_name(),
            'current_month': today.strftime('%B %Y'),
            'total_days': total_days,
            'present_days': present_days,
            'late_days': late_days,
            'absent_days': absent_days,
            'attendance_percentage': round(attendance_percentage, 2)
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        student = self.get_object()
        student.is_active = False
        student.save()
        return Response({'status': 'Student deactivated successfully'})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        student = self.get_object()
        student.is_active = True
        student.save()
        return Response({'status': 'Student activated successfully'})

    @action(detail=False, methods=['get'])
    def recent_admissions(self, request):
        last_30_days = date.today() - timedelta(days=30)
        recent_students = Student.objects.filter(
            admission_date__gte=last_30_days
        ).order_by('-admission_date')[:10]
        serializer = self.get_serializer(recent_students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def birthday_today(self, request):
        today = date.today()
        birthday_students = Student.objects.filter(
            date_of_birth__month=today.month,
            date_of_birth__day=today.day,
            is_active=True
        )
        serializer = self.get_serializer(birthday_students, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total_students = Student.objects.filter(is_active=True).count()
        total_grades = Grade.objects.count()
        total_sections = Section.objects.count()
        
        gender_stats = Student.objects.filter(is_active=True).values('gender').annotate(
            count=Count('id')
        )
        
        grade_stats = Student.objects.filter(is_active=True).values(
            'grade__name'
        ).annotate(count=Count('id'))
        
        return Response({
            'total_students': total_students,
            'total_grades': total_grades,
            'total_sections': total_sections,
            'gender_distribution': list(gender_stats),
            'grade_distribution': list(grade_stats)
        })

class StudentAttendanceViewSet(viewsets.ModelViewSet):
    queryset = StudentAttendance.objects.select_related('student__user', 'recorded_by').all()
    serializer_class = StudentAttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'date', 'status', 'student__grade', 'student__section']
    ordering = ['-date', 'student__roll_number']

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = BulkAttendanceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            attendances = serializer.save()
            return Response({
                'message': f'Successfully recorded attendance for {len(attendances)} students',
                'count': len(attendances)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def daily_report(self, request):
        report_date = request.query_params.get('date', date.today())
        if isinstance(report_date, str):
            from datetime import datetime
            report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        
        attendances = StudentAttendance.objects.filter(date=report_date)
        
        summary = {
            'date': report_date,
            'total_records': attendances.count(),
            'present': attendances.filter(status='P').count(),
            'absent': attendances.filter(status='A').count(),
            'late': attendances.filter(status='L').count(),
            'excused': attendances.filter(status='E').count(),
        }
        
        return Response(summary)

    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        month = request.query_params.get('month', date.today().month)
        year = request.query_params.get('year', date.today().year)
        
        attendances = StudentAttendance.objects.filter(
            date__month=month,
            date__year=year
        )
        
        summary = {
            'month': month,
            'year': year,
            'total_records': attendances.count(),
            'present': attendances.filter(status='P').count(),
            'absent': attendances.filter(status='A').count(),
            'late': attendances.filter(status='L').count(),
            'excused': attendances.filter(status='E').count(),
        }
        
        return Response(summary)

# ================================
# students/urls.py
# ================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GradeViewSet, SectionViewSet, StudentViewSet, StudentAttendanceViewSet

router = DefaultRouter()
router.register(r'grades', GradeViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'', StudentViewSet, basename='student')
router.register(r'attendance', StudentAttendanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

# ================================
# teachers/models.py
# ================================
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    head = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_department')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('FT', 'Full Time'),
        ('PT', 'Part Time'),
        ('CT', 'Contract'),
        ('SB', 'Substitute'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teacher_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teachers')
    employee_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    emergency_contact = models.CharField(max_length=17)
    address = models.TextField()
    qualification = models.CharField(max_length=200)
    experience_years = models.IntegerField(default=0)
    employment_type = models.CharField(max_length=2, choices=EMPLOYMENT_TYPE_CHOICES, default='FT')
    joining_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    subjects = models.ManyToManyField('courses.Subject', blank=True, related_name='teachers')
    profile_picture = models.ImageField(upload_to='teachers/profiles/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.teacher_id})"

class TeacherAttendance(models.Model):
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
        ('HL', 'Half Leave'),
        ('FL', 'Full Leave'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='P')
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    working_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['teacher', 'date']

    def __str__(self):
        return f"{self.teacher} - {self.date} - {self.get_status_display()}"

# ================================
# teachers/serializers.py
# ================================
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Teacher, TeacherAttendance

class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head.user.get_full_name', read_only=True)
    teachers_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = '__all__'

    def get_teachers_count(self, obj):
        return obj.teachers.filter(is_active=True).count()

class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    age = serializers.SerializerMethodField()
    subjects_list = serializers.StringRelatedField(source='subjects', many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = '__all__'

    def get_age(self, obj):
        from datetime import date
        today = date.today()
        return today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))

class TeacherCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Teacher
        exclude = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        user_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
        }
        user = User.objects.create_user(**user_data)
        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher

class TeacherAttendanceSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    teacher_id = serializers.CharField(source='teacher.teacher_id', read_only=True)
    department_name = serializers.CharField(source='teacher.department.name', read_only=True)

    class Meta:
        model = TeacherAttendance
        fields = '__all__'

# ================================
# teachers/views.py
# ================================
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Sum
from datetime import date, timedelta
from .models import Department, Teacher, TeacherAttendance
from .serializers import DepartmentSerializer, TeacherSerializer, TeacherCreateSerializer, TeacherAttendanceSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'code', 'description']

    @action(detail=True, methods=['get'])
    def teachers(self, request, pk=None):
        department = self.get_object()
        teachers = department.teachers.filter(is_active=True)
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        department = self.get_object()
        teachers = department.teachers.filter(is_active=True)
        
        stats = {
            'total_teachers': teachers.count(),
            'avg_experience': teachers.aggregate(Avg('experience_years'))['experience_years__avg'] or 0,
            'employment_types': teachers.values('employment_type').annotate(count=Count('id')),
            'gender_distribution': teachers.values('gender').annotate(count=Count('id'))
        }
        return Response(stats)

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related('user', 'department').prefetch_related('subjects').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'employment_type', 'gender', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'teacher_id', 'employee_id']
    ordering_fields = ['user__first_name', 'joining_date', 'experience_years']

    def get_serializer_class(self):
        if self.action == 'create':
            return TeacherCreateSerializer
        return TeacherSerializer

    @action(detail=True, methods=['get'])
    def attendance_history(self, request, pk=None):
        teacher = self.get_object()
        attendances = TeacherAttendance.objects.filter(teacher=teacher).order_by('-date')
        serializer = TeacherAttendanceSerializer(attendances, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        teacher = self.get_object()
        
        today = date.today()
        first_day = today.replace(day=1)
        
        total_days = TeacherAttendance.objects.filter(
            teacher=teacher, 
            date__gte=first_day
        ).count()
        
        present_days = TeacherAttendance.objects.filter(
            teacher=teacher, 
            date__gte=first_day, 
            status='P'
        ).count()
        
        return Response({
            'teacher_id': teacher.teacher_id,
            'teacher_name': teacher.user.get_full_name(),
            'total_days': total_days,
            'present_days': present_days,
            'attendance_percentage': (present_days / total_days * 100) if total_days > 0 else 0
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        teachers = Teacher.objects.filter(is_active=True)
        
        stats = {
            'total_teachers': teachers.count(),
            'departments': Department.objects.count(),
            'avg_experience': teachers.aggregate(Avg('experience_years'))['experience_years__avg'] or 0,
            'avg_salary': teachers.aggregate(Avg('salary'))['salary__avg'] or 0,
            'employment_distribution': list(teachers.values('employment_type').annotate(count=Count('id'))),
            'department_distribution': list(teachers.values('department__name').annotate(count=Count('id')))
        }
        return Response(stats)

class TeacherAttendanceViewSet(viewsets.ModelViewSet):
    queryset = TeacherAttendance.objects.select_related('teacher__user', 'teacher__department').all()
    serializer_class = TeacherAttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['teacher', 'date', 'status', 'teacher__department']
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def daily_report(self, request):
        report_date = request.query_params.get('date', date.today())
        if isinstance(report_date, str):
            from datetime import datetime
            report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        
        attendances = TeacherAttendance.objects.filter(date=report_date)
        
        summary = {
            'date': report_date,
            'total_records': attendances.count(),
            'present': attendances.filter(status='P').count(),
            'absent': attendances.filter(status='A').count(),
            'late': attendances.filter(status='L').count(),
            'half_leave': attendances.filter(status='HL').count(),
            'full_leave': attendances.filter(status='FL').count(),
            'avg_working_hours': attendances.aggregate(Avg('working_hours'))['working_hours__avg'] or 0
        }
        
        return Response(summary)

# ================================
# teachers/urls.py
# ================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, TeacherViewSet, TeacherAttendanceViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'', TeacherViewSet, basename='teacher')
router.register(r'attendance', TeacherAttendanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

# ================================
# courses/models.py
# ================================
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    credit_hours = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(10)])
    is_mandatory = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Course(models.Model):
    SEMESTER_CHOICES = [
        ('1', 'First Semester'),
        ('2', 'Second Semester'),
        ('3', 'Third Semester'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    grade = models.ForeignKey('students.Grade', on_delete=models.CASCADE, related_name='courses')
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, default='1')
    subjects = models.ManyToManyField(Subject, related_name='courses')
    description = models.TextField(blank=True)
    total_credit_hours = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['grade', 'semester']

    def __str__(self):
        return f"{self.name} - {self.grade.name}"

class Schedule(models.Model):
    DAYS_OF_WEEK = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    section = models.ForeignKey('students.Section', on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['teacher', 'day_of_week', 'start_time']

    def __str__(self):
        return f"{self.subject.name} - {self.day_of_week} {self.start_time}"

# ================================
# courses/serializers.py
# ================================
from rest_framework import serializers
from .models import Subject, Course, Schedule

class SubjectSerializer(serializers.ModelSerializer):
    courses_count = serializers.SerializerMethodField()
    teachers_count = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = '__all__'

    def get_courses_count(self, obj):
        return obj.courses.count()

    def get_teachers_count(self, obj):
        return obj.teachers.count()

class CourseSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    subjects_list = serializers.StringRelatedField(source='subjects', many=True, read_only=True)
    subjects_count = serializers.SerializerMethodField()
    schedules_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_subjects_count(self, obj):
        return obj.subjects.count()

    def get_schedules_count(self, obj):
        return obj.schedules.filter(is_active=True).count()

class ScheduleSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    grade_name = serializers.CharField(source='section.grade.name', read_only=True)

    class Meta:
        model = Schedule
        fields = '__all__'

# ================================
# courses/views.py
# ================================
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from .models import Subject, Course, Schedule
from .serializers import SubjectSerializer, CourseSerializer, ScheduleSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    filterset_fields = ['is_mandatory', 'credit_hours']
    ordering_fields = ['name', 'code', 'credit_hours', 'created_at']

    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        subject = self.get_object()
        courses = subject.courses.filter(is_active=True)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def teachers(self, request, pk=None):
        subject = self.get_object()
        from teachers.serializers import TeacherSerializer
        teachers = subject.teachers.filter(is_active=True)
        serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        stats = Subject.objects.aggregate(
            total_subjects=Count('id'),
            mandatory_subjects=Count('id', filter=models.Q(is_mandatory=True)),
            total_credit_hours=models.Sum('credit_hours')
        )
        return Response(stats)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('grade').prefetch_related('subjects').all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    filterset_fields = ['grade', 'semester', 'is_active']
    ordering_fields = ['name', 'grade__level', 'created_at']

    @action(detail=True, methods=['get'])
    def schedules(self, request, pk=None):
        course = self.get_object()
        schedules = course.schedules.filter(is_active=True).order_by('day_of_week', 'start_time')
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def subjects(self, request, pk=None):
        course = self.get_object()
        subjects = course.subjects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        from students.models import Grade
        stats = {
            'total_courses': Course.objects.filter(is_active=True).count(),
            'courses_by_grade': list(Course.objects.filter(is_active=True).values('grade__name').annotate(count=Count('id'))),
            'courses_by_semester': list(Course.objects.filter(is_active=True).values('semester').annotate(count=Count('id'))),
            'total_subjects': Subject.objects.count()
        }
        return Response(stats)

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.select_related('course', 'subject', 'teacher__user', 'section__grade').all()
    serializer_class = ScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'subject', 'teacher', 'section', 'day_of_week', 'is_active']
    search_fields = ['subject__name', 'teacher__user__first_name', 'room_number']
    ordering = ['day_of_week', 'start_time']

    @action(detail=False, methods=['get'])
    def teacher_schedule(self, request):
        teacher_id = request.query_params.get('teacher_id')
        if not teacher_id:
            return Response({'error': 'teacher_id parameter required'}, status=400)
        
        schedules = Schedule.objects.filter(
            teacher_id=teacher_id, 
            is_active=True
        ).order_by('day_of_week', 'start_time')
        
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def section_schedule(self, request):
        section_id = request.query_params.get('section_id')
        if not section_id:
            return Response({'error': 'section_id parameter required'}, status=400)
        
        schedules = Schedule.objects.filter(
            section_id=section_id, 
            is_active=True
        ).order_by('day_of_week', 'start_time')
        
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def room_schedule(self, request):
        room_number = request.query_params.get('room_number')
        if not room_number:
            return Response({'error': 'room_number parameter required'}, status=400)
        
        schedules = Schedule.objects.filter(
            room_number=room_number, 
            is_active=True
        ).order_by('day_of_week', 'start_time')
        
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def daily_schedule(self, request):
        day = request.query_params.get('day')
        if not day:
            return Response({'error': 'day parameter required'}, status=400)
        
        schedules = Schedule.objects.filter(
            day_of_week=day.upper(), 
            is_active=True
        ).order_by('start_time')
        
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)

# ================================
# courses/urls.py
# ================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, CourseViewSet, ScheduleViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'', CourseViewSet, basename='course')
router.register(r'schedules', ScheduleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

# ================================
# academics/models.py
# ================================
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class ExamType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Exam(models.Model):
    name = models.CharField(max_length=100)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name='exams')
    grade = models.ForeignKey('students.Grade', on_delete=models.CASCADE, related_name='exams')
    subject = models.ForeignKey('courses.Subject', on_delete=models.CASCADE, related_name='exams')
    exam_date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.IntegerField()
    total_marks = models.IntegerField(validators=[MinValueValidator(1)])
    passing_marks = models.IntegerField()
    instructions = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject.name} - {self.grade.name}"

class Result(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('C-', 'C-'),
        ('D', 'D'), ('F', 'F'),
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True)
    is_passed = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'exam']

    def save(self, *args, **kwargs):
        self.percentage = (self.marks_obtained / self.exam.total_marks) * 100
        self.is_passed = self.marks_obtained >= self.exam.passing_marks
        
        # Calculate grade based on percentage
        if self.percentage >= 95:
            self.grade = 'A+'
        elif self.percentage >= 90:
            self.grade = 'A'
        elif self.percentage >= 85:
            self.grade = 'A-'
        elif self.percentage >= 80:
            self.grade = 'B+'
        elif self.percentage >= 75:
            self.grade = 'B'
        elif self.percentage >= 70:
            self.grade = 'B-'
        elif self.percentage >= 65:
            self.grade = 'C+'
        elif self.percentage >= 60:
            self.grade = 'C'
        elif self.percentage >= 55:
            self.grade = 'C-'
        elif self.percentage >= 50:
            self.grade = 'D'
        else:
            self.grade = 'F'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.marks_obtained}/{self.exam.total_marks}"

class Assignment(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('CLOSED', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey('courses.Subject', on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='assignments')
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    total_marks = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    attachment = models.FileField(upload_to='assignments/', blank=True)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='submissions')
    submission_text = models.TextField(blank=True)
    attachment = models.FileField(upload_to='submissions/', blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    is_late = models.BooleanField(default=False)
    graded_by = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['assignment', 'student']

    def save(self, *args, **kwargs):
        if not self.pk:  # Only check on creation
            self.is_late = self.submitted_at > self.assignment.due_date
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.assignment.title}"

# ================================
# academics/serializers.py
# ================================
from rest_framework import serializers
from .models import ExamType, Exam, Result, Assignment, Submission

class ExamTypeSerializer(serializers.ModelSerializer):
    exams_count = serializers.SerializerMethodField()

    class Meta:
        model = ExamType
        fields = '__all__'

    def get_exams_count(self, obj):
        return obj.exams.count()

class ExamSerializer(serializers.ModelSerializer):
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    results_count = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = '__all__'

    def get_results_count(self, obj):
        return obj.results.count()

class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    subject_name = serializers.CharField(source='exam.subject.name', read_only=True)
    total_marks = serializers.CharField(source='exam.total_marks', read_only=True)

    class Meta:
        model = Result
        fields = '__all__'

class AssignmentSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    submissions_count = serializers.SerializerMethodField()
    pending_submissions = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = '__all__'

    def get_submissions_count(self, obj):
        return obj.submissions.count()

    def get_pending_submissions(self, obj):
        from students.models import Student
        total_students = Student.objects.filter(
            grade=obj.course.grade, 
            is_active=True
        ).count()
        return total_students - obj.submissions.count()

class SubmissionSerializer(serializers.ModelSerializer):
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.user.get_full_name', read_only=True)
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = '__all__'

    def get_percentage(self, obj):
        if obj.marks_obtained and obj.assignment.total_marks:
            return round((obj.marks_obtained / obj.assignment.total_marks) * 100, 2)
        return None

# ================================
# academics/views.py
# ================================
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q
from datetime import date, timedelta
from .models import ExamType, Exam, Result, Assignment, Submission
from .serializers import (ExamTypeSerializer, ExamSerializer, ResultSerializer, 
                         AssignmentSerializer, SubmissionSerializer)

class ExamTypeViewSet(viewsets.ModelViewSet):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['