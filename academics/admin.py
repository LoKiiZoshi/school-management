from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from django.urls import reverse
from django.utils import timezone
from .models import ExamType, Exam, Result, Assignment, Submission

@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'weight_percentage', 'exam_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['weight_percentage', 'is_active']
    ordering = ['name']
    
    def exam_count(self, obj):
        return obj.exams.count()
    exam_count.short_description = 'Number of Exams'
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            exam_count=Count('exams')
        )

class ResultInline(admin.TabularInline):
    model = Result
    extra = 0
    readonly_fields = ['percentage', 'grade', 'is_passed']
    fields = ['student', 'marks_obtained', 'percentage', 'grade', 'is_passed', 'remarks']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'student__user')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'subject', 'grade', 'exam_type', 'exam_date', 
        'total_marks', 'results_count', 'average_marks', 'pass_rate', 
        'is_published', 'created_at'
    ]
    list_filter = [
        'exam_type', 'grade', 'subject', 'is_published', 
        'exam_date', 'created_at'
    ]
    search_fields = ['name', 'subject__name', 'grade__name']
    readonly_fields = ['created_at', 'results_count', 'average_marks', 'pass_rate']
    list_editable = ['is_published']
    date_hierarchy = 'exam_date'
    ordering = ['-exam_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'exam_type', 'grade', 'subject')
        }),
        ('Exam Details', {
            'fields': ('exam_date', 'start_time', 'duration_minutes', 'total_marks', 'passing_marks')
        }),
        ('Additional Information', {
            'fields': ('instructions', 'is_published'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('results_count', 'average_marks', 'pass_rate', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [ResultInline]
    
    def results_count(self, obj):
        return obj.results.count()
    results_count.short_description = 'Total Results'
    
    def average_marks(self, obj):
        results = obj.results.all()
        if results.exists():
            avg = results.aggregate(Avg('marks_obtained'))['marks_obtained__avg']
            return f"{avg:.2f}" if avg else "0.00"
        return "0.00"
    average_marks.short_description = 'Average Marks'
    
    def pass_rate(self, obj):
        results = obj.results.all()
        if results.exists():
            passed = results.filter(is_passed=True).count()
            rate = (passed / results.count()) * 100
            color = 'green' if rate >= 70 else 'orange' if rate >= 50 else 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color, rate
            )
        return "0.0%"
    pass_rate.short_description = 'Pass Rate'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'exam_type', 'grade', 'subject'
        ).prefetch_related('results')
    
    actions = ['publish_exams', 'unpublish_exams']
    
    def publish_exams(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(
            request, 
            f'{updated} exam(s) were successfully published.'
        )
    publish_exams.short_description = 'Publish selected exams'
    
    def unpublish_exams(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(
            request, 
            f'{updated} exam(s) were successfully unpublished.'
        )
    unpublish_exams.short_description = 'Unpublish selected exams'

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'exam', 'marks_obtained', 'total_marks', 
        'percentage', 'grade', 'is_passed', 'published_at'
    ]
    list_filter = [
        'grade', 'is_passed', 'exam__exam_type', 'exam__subject', 
        'exam__grade', 'published_at', 'created_at'
    ]
    search_fields = [
        'student__user__first_name', 'student__user__last_name', 
        'student__roll_number', 'exam__name'
    ]
    readonly_fields = ['percentage', 'grade', 'is_passed', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Student & Exam', {
            'fields': ('student', 'exam')
        }),
        ('Marks', {
            'fields': ('marks_obtained', 'total_marks', 'percentage', 'grade', 'is_passed')
        }),
        ('Additional Information', {
            'fields': ('remarks', 'published_at', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def total_marks(self, obj):
        return obj.exam.total_marks
    total_marks.short_description = 'Total Marks'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'student__user', 'exam', 'exam__subject'
        )
    
    actions = ['publish_results', 'unpublish_results']
    
    def publish_results(self, request, queryset):
        updated = queryset.update(published_at=timezone.now())
        self.message_user(
            request, 
            f'{updated} result(s) were successfully published.'
        )
    publish_results.short_description = 'Publish selected results'
    
    def unpublish_results(self, request, queryset):
        updated = queryset.update(published_at=None)
        self.message_user(
            request, 
            f'{updated} result(s) were successfully unpublished.'
        )
    unpublish_results.short_description = 'Unpublish selected results'

class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ['submitted_at', 'is_late']
    fields = [
        'student', 'submission_text', 'attachment', 'submitted_at', 
        'is_late', 'marks_obtained', 'feedback'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'student__user')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'subject', 'course', 'teacher', 'assigned_date', 
        'due_date', 'total_marks', 'status', 'submissions_count', 
        'graded_count', 'is_overdue'
    ]
    list_filter = [
        'status', 'course', 'subject', 'teacher', 
        'assigned_date', 'due_date'
    ]
    search_fields = ['title', 'description', 'subject__name', 'course__name']
    readonly_fields = ['assigned_date', 'created_at', 'submissions_count', 'graded_count']
    date_hierarchy = 'due_date'
    ordering = ['-assigned_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'course', 'subject', 'teacher')
        }),
        ('Assignment Details', {
            'fields': ('due_date', 'total_marks', 'status', 'attachment', 'instructions')
        }),
        ('Timestamps', {
            'fields': ('assigned_date', 'created_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('submissions_count', 'graded_count'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [SubmissionInline]
    
    def submissions_count(self, obj):
        return obj.submissions.count()
    submissions_count.short_description = 'Total Submissions'
    
    def graded_count(self, obj):
        return obj.submissions.filter(marks_obtained__isnull=False).count()
    graded_count.short_description = 'Graded Submissions'
    
    def is_overdue(self, obj):
        if timezone.now() > obj.due_date:
            return format_html('<span style="color: red;">Yes</span>')
        return format_html('<span style="color: green;">No</span>')
    is_overdue.short_description = 'Overdue'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'course', 'subject', 'teacher', 'teacher__user'
        ).prefetch_related('submissions')
    
    actions = ['publish_assignments', 'close_assignments']
    
    def publish_assignments(self, request, queryset):
        updated = queryset.update(status='PUBLISHED')
        self.message_user(
            request, 
            f'{updated} assignment(s) were successfully published.'
        )
    publish_assignments.short_description = 'Publish selected assignments'
    
    def close_assignments(self, request, queryset):
        updated = queryset.update(status='CLOSED')
        self.message_user(
            request, 
            f'{updated} assignment(s) were successfully closed.'
        )
    close_assignments.short_description = 'Close selected assignments'

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'assignment', 'submitted_at', 'marks_obtained', 
        'total_marks', 'percentage', 'is_late', 'graded_by', 'status'
    ]
    list_filter = [
        'is_late', 'assignment__status', 'assignment__subject', 
        'assignment__course', 'graded_by', 'submitted_at'
    ]
    search_fields = [
        'student__user__first_name', 'student__user__last_name', 
        'student__roll_number', 'assignment__title'
    ]
    readonly_fields = ['submitted_at', 'is_late', 'graded_at', 'percentage']
    date_hierarchy = 'submitted_at'
    ordering = ['-submitted_at']
    
    fieldsets = (
        ('Student & Assignment', {
            'fields': ('student', 'assignment')
        }),
        ('Submission Details', {
            'fields': ('submission_text', 'attachment', 'submitted_at', 'is_late')
        }),
        ('Grading', {
            'fields': ('marks_obtained', 'percentage', 'feedback', 'graded_by', 'graded_at')
        })
    )
    
    def total_marks(self, obj):
        return obj.assignment.total_marks
    total_marks.short_description = 'Total Marks'
    
    def percentage(self, obj):
        if obj.marks_obtained and obj.assignment.total_marks:
            return f"{(obj.marks_obtained / obj.assignment.total_marks) * 100:.1f}%"
        return "Not Graded"
    percentage.short_description = 'Percentage'
    
    def status(self, obj):
        if obj.marks_obtained is not None:
            color = 'green'
            text = 'Graded'
        elif obj.is_late:
            color = 'orange'
            text = 'Late Submission'
        else:
            color = 'blue'
            text = 'Pending Review'
        
        return format_html(
            '<span style="color: {};">{}</span>',
            color, text
        )
    status.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'student__user', 'assignment', 'assignment__subject',
            'graded_by', 'graded_by__user'
        )
    
    def save_model(self, request, obj, form, change):
        if obj.marks_obtained is not None and not obj.graded_by:
            obj.graded_by = request.user.teacher_profile
            obj.graded_at = timezone.now()
        super().save_model(request, obj, form, change)

# Custom admin site configuration
admin.site.site_header = 'Exam Management System'
admin.site.site_title = 'Exam Admin'
admin.site.index_title = 'Welcome to Exam Management System'

# Register additional admin configurations
class ExamTypeFilter(admin.SimpleListFilter):
    title = 'exam type'
    parameter_name = 'exam_type'
    
    def lookups(self, request, model_admin):
        return ExamType.objects.values_list('id', 'name')
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(exam_type_id=self.value())
        return queryset

class GradeFilter(admin.SimpleListFilter):
    title = 'grade status'
    parameter_name = 'grade_status'
    
    def lookups(self, request, model_admin):
        return [
            ('passed', 'Passed'),
            ('failed', 'Failed'),
            ('excellent', 'Excellent (A+/A)'),
            ('good', 'Good (B+/B/B-)'),
            ('average', 'Average (C+/C/C-)'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'passed':
            return queryset.filter(is_passed=True)
        elif self.value() == 'failed':
            return queryset.filter(is_passed=False)
        elif self.value() == 'excellent':
            return queryset.filter(grade__in=['A+', 'A'])
        elif self.value() == 'good':
            return queryset.filter(grade__in=['B+', 'B', 'B-'])
        elif self.value() == 'average':
            return queryset.filter(grade__in=['C+', 'C', 'C-'])
        return queryset