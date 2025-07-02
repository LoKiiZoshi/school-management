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
