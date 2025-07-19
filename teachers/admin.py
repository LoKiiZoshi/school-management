from django.contrib import admin
from .models import Department, Teacher, TeacherAttendance

# Optional: Customize how Department appears in admin
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'head', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('created_at',)

# Optional: Customize how Teacher appears in admin
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'teacher_id', 'department', 'employment_type', 'salary', 'is_active', 'joining_date')
    search_fields = ('teacher_id', 'user__username', 'user__first_name', 'user__last_name')
    list_filter = ('department', 'employment_type', 'is_active')
    filter_horizontal = ('subjects',)  # for ManyToManyField UI

# Optional: Customize how TeacherAttendance appears in admin
@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'status', 'check_in_time', 'check_out_time', 'working_hours')
    search_fields = ('teacher__user__first_name', 'teacher__teacher_id')
    list_filter = ('status', 'date')
