from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Employee, Task, TaskCategory, TaskComment, TaskSchedule, EmailLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
 

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        
        

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Employee
        fields = '__all__'
        
        

class TaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = '__all__'
        
        

class TaskCommentSerializer(serializers.ModelSerializer):
    author = EmployeeSerializer(read_only=True)
    
    class Meta:
        model = TaskComment
        fields = '__all__'
        


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.user.get_full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.user.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'



class TaskScheduleSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.user.get_full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.user.get_full_name', read_only=True)
    
    class Meta:
        model = TaskSchedule
        fields = '__all__'
        


class EmailLogSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source='recipient.user.get_full_name', read_only=True)
    
    class Meta:
        model = EmailLog
        fields = '__all__'
