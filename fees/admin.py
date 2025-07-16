from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import *

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'phone', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'code', 'email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'address', 'phone', 'email', 'website', 'logo')
        }),
        ('Administrative', {
            'fields': ('established_date', 'principal_name', 'status')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'start_date', 'end_date', 'is_current', 'created_at')
    list_filter = ('is_current', 'start_date', 'school')
    search_fields = ('name', 'school__name')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'section', 'school', 'capacity', 'student_count', 'class_teacher')
    list_filter = ('grade', 'school', 'created_at')
    search_fields = ('name', 'grade', 'section', 'school__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def student_count(self, obj):
        return obj.students.filter(is_active=True).count()
    student_count.short_description = 'Students'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_full_name', 'current_class', 'school', 'status', 'admission_date')
    list_filter = ('status', 'current_class', 'school', 'admission_date')
    search_fields = ('student_id', 'user__first_name', 'user__last_name', 'admission_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('class_grade', 'fee_type', 'amount', 'due_date', 'is_mandatory', 'school')
    list_filter = ('fee_type', 'is_mandatory', 'school', 'academic_year')
    search_fields = ('class_grade__name', 'fee_type', 'school__name')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_fee_type', 'amount_due', 'amount_paid', 'payment_status', 'due_date')
    list_filter = ('payment_status', 'fee_structure__fee_type', 'due_date', 'school')
    search_fields = ('student__student_id', 'student__user__first_name', 'student__user__last_name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'total_amount', 'balance_amount')
    
    def get_fee_type(self, obj):
        return obj.fee_structure.get_fee_type_display()
    get_fee_type.short_description = 'Fee Type'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'student', 'amount', 'payment_method', 'payment_date', 'collected_by')
    list_filter = ('payment_method', 'payment_date', 'school')
    search_fields = ('receipt_number', 'student__student_id', 'student__user__first_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def view_receipt(self, obj):
        url = reverse('admin:fees_payment_change', args=[obj.id])
        return format_html('<a href="{}">View Receipt</a>', url)
    view_receipt.short_description = 'Receipt'

@admin.register(PaymentDetail)
class PaymentDetailAdmin(admin.ModelAdmin):
    list_display = ('payment', 'get_student', 'get_fee_type', 'amount')
    list_filter = ('payment__payment_date', 'student_fee__fee_structure__fee_type')
    search_fields = ('payment__receipt_number', 'student_fee__student__student_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def get_student(self, obj):
        return obj.student_fee.student
    get_student.short_description = 'Student'
    
    def get_fee_type(self, obj):
        return obj.student_fee.fee_structure.get_fee_type_display()
    get_fee_type.short_description = 'Fee Type'

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_type', 'value', 'valid_from', 'valid_until', 'school')
    list_filter = ('discount_type', 'valid_from', 'valid_until', 'school')
    search_fields = ('name', 'description', 'school__name')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(StudentDiscount)
class StudentDiscountAdmin(admin.ModelAdmin):
    list_display = ('student', 'discount', 'approved_by', 'approved_date')
    list_filter = ('approved_date', 'discount', 'approved_by')
    search_fields = ('student__student_id', 'discount__name', 'approved_by__username')
    readonly_fields = ('id', 'created_at', 'updated_at')