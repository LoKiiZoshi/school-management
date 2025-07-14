from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Teacher, TeacherAttendance

class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head.user.get_full_name', read_only=True)
    teachers_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = '__all__'

    def get_teachers_count(self, obj):
        return obj.teachers.filter(is_active=True).count()

class TeacherSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    age = serializers.SerializerMethodField()
    subjects_list = serializers.StringRelatedField(source='subjects', many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = '__all__'

    def get_age(self, obj):
        from datetime import date
        today = date.today()
        return today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))

class TeacherCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Teacher
        exclude = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        user_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
        }
        user = User.objects.create_user(**user_data)
        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher

class TeacherAttendanceSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    teacher_id = serializers.CharField(source='teacher.teacher_id', read_only=True)
    department_name = serializers.CharField(source='teacher.department.name', read_only=True)

    class Meta:
        model = TeacherAttendance
        fields = '__all__'