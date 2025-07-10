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
