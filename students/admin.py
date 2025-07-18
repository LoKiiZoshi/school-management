from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Grade, Section, Student, StudentAttendance


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'section_count', 'student_count', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['level']
    readonly_fields = ['created_at']
    
    def section_count(self, obj):
        return obj.sections.count()
    section_count.short_description = 'Sections'
    
    def student_count(self, obj):
        return Student.objects.filter(grade=obj).count()
    student_count.short_description = 'Students'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'capacity', 'current_students', 'room_number']
    list_filter = ['grade', 'capacity']
    search_fields = ['name', 'grade__name', 'room_number']
    ordering = ['grade__level', 'name']
    
    def current_students(self, obj):
        count = obj.student_set.count()
        if count > obj.capacity:
            return format_html(
                '<span style="color: red; font-weight: bold;">{}/{}</span>',
                count, obj.capacity
            )
        elif count == obj.capacity:
            return format_html(
                '<span style="color: orange; font-weight: bold;">{}/{}</span>',
                count, obj.capacity
            )
        return f"{count}/{obj.capacity}"
    current_students.short_description = 'Current/Capacity'


class StudentAttendanceInline(admin.TabularInline):
    model = StudentAttendance
    extra = 0
    readonly_fields = ['created_at']
    fields = ['date', 'status', 'remarks', 'recorded_by', 'created_at']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'student_id', 'full_name', 'grade', 'section', 'roll_number', 
        'gender', 'attendance_summary', 'is_active', 'created_at'
    ]
    list_filter = [
        'grade', 'section', 'gender', 'blood_group', 'is_active', 
        'admission_date', 'created_at'
    ]
    search_fields = [
        'student_id', 'user__first_name', 'user__last_name', 
        'user__email', 'admission_number', 'roll_number', 
        'parent_name', 'parent_email'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'profile_picture_preview'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user', 'student_id', 'admission_number', 'admission_date',
                'profile_picture', 'profile_picture_preview'
            )
        }),
        ('Academic Details', {
            'fields': ('grade', 'section', 'roll_number', 'is_active')
        }),
        ('Personal Information', {
            'fields': (
                'date_of_birth', 'gender', 'blood_group', 
                'phone_number', 'address', 'emergency_contact'
            )
        }),
        ('Parent/Guardian Information', {
            'fields': ('parent_name', 'parent_email', 'parent_phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [StudentAttendanceInline]
    
    def full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'user__first_name'
    
    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return "No image"
    profile_picture_preview.short_description = 'Profile Picture Preview'
    
    def attendance_summary(self, obj):
        total_days = obj.attendances.count()
        if total_days == 0:
            return "No records"
        
        present_days = obj.attendances.filter(status='P').count()
        late_days = obj.attendances.filter(status='L').count()
        
        attendance_rate = ((present_days + late_days) / total_days) * 100
        
        color = 'green' if attendance_rate >= 90 else 'orange' if attendance_rate >= 75 else 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span> ({}/{})',
            color, attendance_rate, present_days + late_days, total_days
        )
    attendance_summary.short_description = 'Attendance'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new student
            # Set username as student_id if user doesn't have one
            if not obj.user.username:
                obj.user.username = obj.student_id
                obj.user.save()
        super().save_model(request, obj, form, change)
    
    actions = ['mark_active', 'mark_inactive']
    
    def mark_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request, 
            f'{updated} student(s) marked as active.'
        )
    mark_active.short_description = "Mark selected students as active"
    
    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request, 
            f'{updated} student(s) marked as inactive.'
        )
    mark_inactive.short_description = "Mark selected students as inactive"


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'date', 'status', 'recorded_by', 'created_at'
    ]
    list_filter = [
        'status', 'date', 'student__grade', 'student__section', 
        'recorded_by', 'created_at'
    ]
    search_fields = [
        'student__user__first_name', 'student__user__last_name',
        'student__student_id', 'student__admission_number'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Attendance Details', {
            'fields': ('student', 'date', 'status', 'remarks')
        }),
        ('Record Information', {
            'fields': ('recorded_by', 'created_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.recorded_by:
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['mark_present', 'mark_absent', 'mark_late', 'mark_excused']
    
    def mark_present(self, request, queryset):
        updated = queryset.update(status='P')
        self.message_user(request, f'{updated} attendance record(s) marked as Present.')
    mark_present.short_description = "Mark selected records as Present"
    
    def mark_absent(self, request, queryset):
        updated = queryset.update(status='A')
        self.message_user(request, f'{updated} attendance record(s) marked as Absent.')
    mark_absent.short_description = "Mark selected records as Absent"
    
    def mark_late(self, request, queryset):
        updated = queryset.update(status='L')
        self.message_user(request, f'{updated} attendance record(s) marked as Late.')
    mark_late.short_description = "Mark selected records as Late"
    
    def mark_excused(self, request, queryset):
        updated = queryset.update(status='E')
        self.message_user(request, f'{updated} attendance record(s) marked as Excused.')
    mark_excused.short_description = "Mark selected records as Excused"


# Customize the admin site header and title
admin.site.site_header = "Student Management System"
admin.site.site_title = "SMS Admin"
admin.site.index_title = "Welcome to Student Management System Administration"