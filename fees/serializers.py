from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address', 
                 'date_of_birth', 'gender', 'profile_picture', 'school']
        read_only_fields = ('id',)

class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class ClassSerializer(serializers.ModelSerializer):
    class_teacher_name = serializers.CharField(source='class_teacher.get_full_name', read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_student_count(self, obj):
        return obj.students.filter(is_active=True).count()

class StudentSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    class_name = serializers.CharField(source='current_class.name', read_only=True)
    total_fees_due = serializers.SerializerMethodField()
    total_fees_paid = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_total_fees_due(self, obj):
        return obj.fees.aggregate(total=models.Sum('amount_due'))['total'] or 0
    
    def get_total_fees_paid(self, obj):
        return obj.fees.aggregate(total=models.Sum('amount_paid'))['total'] or 0

class FeeStructureSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_grade.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    fee_type_display = serializers.CharField(source='get_fee_type_display', read_only=True)
    
    class Meta:
        model = FeeStructure
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class StudentFeeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    fee_type_display = serializers.CharField(source='fee_structure.get_fee_type_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    total_amount = serializers.ReadOnlyField()
    balance_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = StudentFee
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class PaymentDetailSerializer(serializers.ModelSerializer):
    fee_type = serializers.CharField(source='student_fee.fee_structure.get_fee_type_display', read_only=True)
    
    class Meta:
        model = PaymentDetail
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    collected_by_name = serializers.CharField(source='collected_by.get_full_name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    payment_details = PaymentDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'receipt_number')
    
    def create(self, validated_data):
        # Auto-generate receipt number
        validated_data['receipt_number'] = f"RCP{timezone.now().strftime('%Y%m%d')}{Payment.objects.count() + 1:04d}"
        return super().create(validated_data)

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class StudentDiscountSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    discount_name = serializers.CharField(source='discount.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = StudentDiscount
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
