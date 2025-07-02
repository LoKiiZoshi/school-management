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