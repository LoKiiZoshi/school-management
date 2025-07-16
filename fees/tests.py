from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

# Base Abstract Model with Timestamp
class BaseModel(models.Model):
    """Base model with common fields for all models"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

# Choice Classes
class StatusChoices(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    SUSPENDED = 'suspended', 'Suspended'

class PaymentStatusChoices(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PAID = 'paid', 'Paid'
    PARTIAL = 'partial', 'Partial'
    OVERDUE = 'overdue', 'Overdue'
    CANCELLED = 'cancelled', 'Cancelled'

class PaymentMethodChoices(models.TextChoices):
    CASH = 'cash', 'Cash'
    CARD = 'card', 'Card'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    ONLINE = 'online', 'Online'
    CHEQUE = 'cheque', 'Cheque'

class FeeTypeChoices(models.TextChoices):
    TUITION = 'tuition', 'Tuition Fee'
    ADMISSION = 'admission', 'Admission Fee'
    EXAMINATION = 'examination', 'Examination Fee'
    LIBRARY = 'library', 'Library Fee'
    LABORATORY = 'laboratory', 'Laboratory Fee'
    TRANSPORT = 'transport', 'Transport Fee'
    HOSTEL = 'hostel', 'Hostel Fee'
    ACTIVITY = 'activity', 'Activity Fee'
    MISCELLANEOUS = 'miscellaneous', 'Miscellaneous'

class GradeChoices(models.TextChoices):
    GRADE_1 = 'grade_1', 'Grade 1'
    GRADE_2 = 'grade_2', 'Grade 2'
    GRADE_3 = 'grade_3', 'Grade 3'
    GRADE_4 = 'grade_4', 'Grade 4'
    GRADE_5 = 'grade_5', 'Grade 5'
    GRADE_6 = 'grade_6', 'Grade 6'
    GRADE_7 = 'grade_7', 'Grade 7'
    GRADE_8 = 'grade_8', 'Grade 8'
    GRADE_9 = 'grade_9', 'Grade 9'
    GRADE_10 = 'grade_10', 'Grade 10'
    GRADE_11 = 'grade_11', 'Grade 11'
    GRADE_12 = 'grade_12', 'Grade 12'

class GenderChoices(models.TextChoices):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'
    OTHER = 'other', 'Other'

# Multi-tenant School Model
class School(BaseModel):
    """School model for multi-tenancy"""
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    established_date = models.DateField()
    principal_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    
    class Meta:
        db_table = 'schools'
        verbose_name = 'School'
        verbose_name_plural = 'Schools'
        
    def __str__(self):
        return self.name

# User Model
class User(AbstractUser):
    """Custom User model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='users')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    class Meta:
        db_table = 'users'

# Academic Year Model
class AcademicYear(BaseModel):
    """Academic Year model"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='academic_years')
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'academic_years'
        unique_together = ['school', 'name']
        
    def __str__(self):
        return f"{self.school.name} - {self.name}"

# Class Model
class Class(BaseModel):
    """Class model"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=20, choices=GradeChoices.choices)
    section = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    class_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teaching_classes')
    
    class Meta:
        db_table = 'classes'
        unique_together = ['school', 'grade', 'section']
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        
    def __str__(self):
        return f"{self.grade} - {self.section}"

# Student Model
class Student(BaseModel):
    """Student model"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    admission_number = models.CharField(max_length=50)
    admission_date = models.DateField()
    current_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, related_name='students')
    parent_name = models.CharField(max_length=255)
    parent_phone = models.CharField(max_length=20)
    parent_email = models.EmailField(blank=True)
    emergency_contact = models.CharField(max_length=20)
    medical_info = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    
    class Meta:
        db_table = 'students'
        unique_together = ['school', 'student_id']
        
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

# Fee Structure Model
class FeeStructure(BaseModel):
    """Fee Structure model"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_structures')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='fee_structures')
    class_grade = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='fee_structures')
    fee_type = models.CharField(max_length=30, choices=FeeTypeChoices.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    due_date = models.DateField()
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'fee_structures'
        unique_together = ['school', 'academic_year', 'class_grade', 'fee_type']
        
    def __str__(self):
        return f"{self.class_grade} - {self.get_fee_type_display()} - {self.amount}"

# Student Fee Model
class StudentFee(BaseModel):
    """Student Fee model"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='student_fees')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='student_fees')
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices.choices, default=PaymentStatusChoices.PENDING)
    due_date = models.DateField()
    remarks = models.TextField(blank=True)
    
    class Meta:
        db_table = 'student_fees'
        unique_together = ['student', 'fee_structure']
        
    def __str__(self):
        return f"{self.student.student_id} - {self.fee_structure.get_fee_type_display()}"
    
    @property
    def total_amount(self):
        return self.amount_due + self.fine_amount - self.discount_amount
    
    @property
    def balance_amount(self):
        return self.total_amount - self.amount_paid

# Payment Model
class Payment(BaseModel):
    """Payment model"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='payments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    receipt_number = models.CharField(max_length=50, unique=True)
    payment_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_method = models.CharField(max_length=20, choices=PaymentMethodChoices.choices)
    transaction_id = models.CharField(max_length=100, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='collected_payments')
    remarks = models.TextField(blank=True)
    
    class Meta:
        db_table = 'payments'
        
    def __str__(self):
        return f"{self.receipt_number} - {self.student.student_id} - {self.amount}"

# Payment Detail Model
class PaymentDetail(BaseModel):
    """Payment Detail model"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='payment_details')
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='payment_details')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    class Meta:
        db_table = 'payment_details'
        
    def __str__(self):
        return f"{self.payment.receipt_number} - {self.student_fee.fee_structure.get_fee_type_display()}"

# Discount Model
class Discount(BaseModel):
    """Discount model"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='discounts')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=[
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ])
    value = models.DecimalField(max_digits=10, decimal_places=2)
    applicable_fee_types = models.CharField(max_length=500, help_text="Comma-separated fee types")
    valid_from = models.DateField()
    valid_until = models.DateField()
    
    class Meta:
        db_table = 'discounts'
        
    def __str__(self):
        return self.name

# Student Discount Model
class StudentDiscount(BaseModel):
    """Student Discount model"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='discounts')
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, related_name='student_discounts')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_discounts')
    approved_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_discounts'
        unique_together = ['student', 'discount']
        
    def __str__(self):
        return f"{self.student.student_id} - {self.discount.name}"
