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