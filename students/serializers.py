from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Grade, Section, Student, StudentAttendance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class GradeSerializer(serializers.ModelSerializer):
    sections_count = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = '__all__'

    def get_sections_count(self, obj):
        return obj.sections.count()

class SectionSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = '__all__'

    def get_students_count(self, obj):
        return obj.student_set.count()

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'

    def get_age(self, obj):
        from datetime import date
        today = date.today()
        return today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))

class StudentCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)

    class Meta:
        model = Student
        exclude = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        user_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
        }
        user = User.objects.create_user(**user_data)
        student = Student.objects.create(user=user, **validated_data)
        return student

class StudentAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)

    class Meta:
        model = StudentAttendance
        fields = '__all__'

class BulkAttendanceSerializer(serializers.Serializer):
    date = serializers.DateField()
    attendances = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

    def create(self, validated_data):
        date = validated_data['date']
        attendances_data = validated_data['attendances']
        user = self.context['request'].user
        
        attendance_objects = []
        for attendance_data in attendances_data:
            student_id = attendance_data['student_id']
            status = attendance_data['status']
            remarks = attendance_data.get('remarks', '')
            
            try:
                student = Student.objects.get(student_id=student_id)
                attendance, created = StudentAttendance.objects.get_or_create(
                    student=student,
                    date=date,
                    defaults={
                        'status': status,
                        'remarks': remarks,
                        'recorded_by': user
                    }
                )
                if not created:
                    attendance.status = status
                    attendance.remarks = remarks
                    attendance.recorded_by = user
                    attendance.save()
                attendance_objects.append(attendance)
            except Student.DoesNotExist:
                continue
        
        return attendance_objects