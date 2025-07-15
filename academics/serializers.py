from rest_framework import serializers
from .models import ExamType, Exam, Result, Assignment, Submission

class ExamTypeSerializer(serializers.ModelSerializer):
    exams_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ExamType
        fields = ['id', 'name', 'description', 'weight_percentage', 'is_active', 'exams_count']
    
    def get_exams_count(self, obj):
        return obj.exams.count()

class ExamSerializer(serializers.ModelSerializer):
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    results_count = serializers.SerializerMethodField()
    average_marks = serializers.SerializerMethodField()
    pass_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'exam_type', 'exam_type_name', 
            'grade', 'grade_name', 'subject', 'subject_name',
            'exam_date', 'start_time', 'duration_minutes', 
            'total_marks', 'passing_marks', 'instructions',
            'is_published', 'created_at', 'results_count',
            'average_marks', 'pass_rate'
        ]
    
    def get_results_count(self, obj):
        return obj.results.count()
    
    def get_average_marks(self, obj):
        results = obj.results.all()
        if results.exists():
            return round(sum(r.marks_obtained for r in results) / results.count(), 2)
        return 0
    
    def get_pass_rate(self, obj):
        results = obj.results.all()
        if results.exists():
            passed = results.filter(is_passed=True).count()
            return round((passed / results.count()) * 100, 2)
        return 0
    
    def validate(self, data):
        # Validate that passing marks is not greater than total marks
        if data.get('passing_marks') and data.get('total_marks'):
            if data['passing_marks'] > data['total_marks']:
                raise serializers.ValidationError(
                    "Passing marks cannot be greater than total marks"
                )
        
        # Validate exam date is not in the past (for new exams)
        if not self.instance and data.get('exam_date'):
            from django.utils import timezone
            if data['exam_date'] < timezone.now().date():
                raise serializers.ValidationError(
                    "Exam date cannot be in the past"
                )
        
        return data

class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_roll_number = serializers.CharField(source='student.roll_number', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    subject_name = serializers.CharField(source='exam.subject.name', read_only=True)
    exam_type_name = serializers.CharField(source='exam.exam_type.name', read_only=True)
    total_marks = serializers.IntegerField(source='exam.total_marks', read_only=True)
    
    class Meta:
        model = Result
        fields = [
            'id', 'student', 'student_name', 'student_roll_number',
            'exam', 'exam_name', 'subject_name', 'exam_type_name',
            'marks_obtained', 'total_marks', 'percentage', 'grade',
            'is_passed', 'remarks', 'published_at', 'created_at'
        ]
        read_only_fields = ['percentage', 'grade', 'is_passed']
    
    def validate(self, data):
        # Validate marks obtained is not greater than total marks
        if data.get('marks_obtained') and data.get('exam'):
            if data['marks_obtained'] > data['exam'].total_marks:
                raise serializers.ValidationError(
                    "Marks obtained cannot be greater than total marks"
                )
        
        # Validate marks obtained is not negative
        if data.get('marks_obtained') and data['marks_obtained'] < 0:
            raise serializers.ValidationError(
                "Marks obtained cannot be negative"
            )
        
        return data

class AssignmentSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    submissions_count = serializers.SerializerMethodField()
    graded_submissions_count = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'course', 'course_name',
            'subject', 'subject_name', 'teacher', 'teacher_name',
            'assigned_date', 'due_date', 'total_marks', 'status',
            'attachment', 'instructions', 'created_at',
            'submissions_count', 'graded_submissions_count', 'is_overdue'
        ]
    
    def get_submissions_count(self, obj):
        return obj.submissions.count()
    
    def get_graded_submissions_count(self, obj):
        return obj.submissions.filter(marks_obtained__isnull=False).count()
    
    def get_is_overdue(self, obj):
        from django.utils import timezone
        return timezone.now() > obj.due_date
    
    def validate(self, data):
        # Validate due date is not in the past
        if data.get('due_date'):
            from django.utils import timezone
            if data['due_date'] < timezone.now():
                raise serializers.ValidationError(
                    "Due date cannot be in the past"
                )
        
        return data

class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_roll_number = serializers.CharField(source='student.roll_number', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    assignment_total_marks = serializers.IntegerField(source='assignment.total_marks', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.user.get_full_name', read_only=True)
    percentage = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'assignment_title', 'assignment_total_marks',
            'student', 'student_name', 'student_roll_number',
            'submission_text', 'attachment', 'submitted_at',
            'marks_obtained', 'percentage', 'feedback', 'is_late',
            'graded_by', 'graded_by_name', 'graded_at', 'status'
        ]
        read_only_fields = ['is_late', 'graded_by', 'graded_at']
    
    def get_percentage(self, obj):
        if obj.marks_obtained and obj.assignment.total_marks:
            return round((obj.marks_obtained / obj.assignment.total_marks) * 100, 2)
        return None
    
    def get_status(self, obj):
        if obj.marks_obtained is not None:
            return 'Graded'
        elif obj.is_late:
            return 'Late Submission'
        else:
            return 'Pending Review'
    
    def validate(self, data):
        # Validate marks obtained is not greater than assignment total marks
        if data.get('marks_obtained') and data.get('assignment'):
            if data['marks_obtained'] > data['assignment'].total_marks:
                raise serializers.ValidationError(
                    "Marks obtained cannot be greater than assignment total marks"
                )
        
        # Validate marks obtained is not negative
        if data.get('marks_obtained') and data['marks_obtained'] < 0:
            raise serializers.ValidationError(
                "Marks obtained cannot be negative"
            )
        
        # Validate that either submission_text or attachment is provided
        if not data.get('submission_text') and not data.get('attachment'):
            raise serializers.ValidationError(
                "Either submission text or attachment must be provided"
            )
        
        return data

# Additional serializers for specific use cases
class ExamResultSummarySerializer(serializers.ModelSerializer):
    """Serializer for exam results summary"""
    results_count = serializers.SerializerMethodField()
    highest_marks = serializers.SerializerMethodField()
    lowest_marks = serializers.SerializerMethodField()
    average_marks = serializers.SerializerMethodField()
    pass_rate = serializers.SerializerMethodField()
    grade_distribution = serializers.SerializerMethodField()
    
    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'exam_date', 'total_marks', 'passing_marks',
            'results_count', 'highest_marks', 'lowest_marks', 
            'average_marks', 'pass_rate', 'grade_distribution'
        ]
    
    def get_results_count(self, obj):
        return obj.results.count()
    
    def get_highest_marks(self, obj):
        result = obj.results.order_by('-marks_obtained').first()
        return result.marks_obtained if result else 0
    
    def get_lowest_marks(self, obj):
        result = obj.results.order_by('marks_obtained').first()
        return result.marks_obtained if result else 0
    
    def get_average_marks(self, obj):
        results = obj.results.all()
        if results.exists():
            return round(sum(r.marks_obtained for r in results) / results.count(), 2)
        return 0
    
    def get_pass_rate(self, obj):
        results = obj.results.all()
        if results.exists():
            passed = results.filter(is_passed=True).count()
            return round((passed / results.count()) * 100, 2)
        return 0
    
    def get_grade_distribution(self, obj):
        distribution = {}
        for grade_choice in Result.GRADE_CHOICES:
            grade_code = grade_choice[0]
            count = obj.results.filter(grade=grade_code).count()
            distribution[grade_code] = count
        return distribution

class StudentResultSerializer(serializers.ModelSerializer):
    """Serializer for student's individual results"""
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    subject_name = serializers.CharField(source='exam.subject.name', read_only=True)
    exam_type_name = serializers.CharField(source='exam.exam_type.name', read_only=True)
    exam_date = serializers.DateField(source='exam.exam_date', read_only=True)
    total_marks = serializers.IntegerField(source='exam.total_marks', read_only=True)
    
    class Meta:
        model = Result
        fields = [
            'id', 'exam_name', 'subject_name', 'exam_type_name',
            'exam_date', 'marks_obtained', 'total_marks', 
            'percentage', 'grade', 'is_passed', 'remarks'
        ]

class AssignmentSubmissionSummarySerializer(serializers.ModelSerializer):
    """Serializer for assignment submission summary"""
    total_submissions = serializers.SerializerMethodField()
    graded_submissions = serializers.SerializerMethodField()
    pending_submissions = serializers.SerializerMethodField()
    late_submissions = serializers.SerializerMethodField()
    average_marks = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'due_date', 'total_marks',
            'total_submissions', 'graded_submissions', 
            'pending_submissions', 'late_submissions', 'average_marks'
        ]
    
    def get_total_submissions(self, obj):
        return obj.submissions.count()
    
    def get_graded_submissions(self, obj):
        return obj.submissions.filter(marks_obtained__isnull=False).count()
    
    def get_pending_submissions(self, obj):
        return obj.submissions.filter(marks_obtained__isnull=True).count()
    
    def get_late_submissions(self, obj):
        return obj.submissions.filter(is_late=True).count()
    
    def get_average_marks(self, obj):
        submissions = obj.submissions.filter(marks_obtained__isnull=False)
        if submissions.exists():
            return round(sum(s.marks_obtained for s in submissions) / submissions.count(), 2)
        return 0