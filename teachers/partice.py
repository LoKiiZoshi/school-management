from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department,Teacher,TeacherAttendance


class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source = 'head.user.get_full_name',read_only = True)
    teacher_count = serializers.serializer