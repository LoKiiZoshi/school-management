from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import *
from .serializers import *
from .permissions import IsSchoolOwnerOrReadOnly, IsAuthenticated

class BaseViewSet(viewsets.ModelViewSet):
    """Base ViewSet with common functionality"""
    permission_classes = [IsAuthenticated, IsSchoolOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset by school for multi-tenancy"""
        if hasattr(self.request.user, 'school'):
            return super().get_queryset().filter(school=self.request.user.school)
        return super().get_queryset().none()
    
    def perform_create(self, serializer):
        """Auto-assign school on creation"""
        if hasattr(self.request.user, 'school'):
            serializer.save(school=self.request.user.school)

class SchoolViewSet(viewsets.ModelViewSet):
    """School ViewSet"""
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'code', 'email']
    filterset_fields = ['status']
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get school dashboard statistics"""
        school = self.get_object()
        stats = {
            'total_students': school.students.filter(is_active=True).count(),
            'total_classes': school.classes.filter(is_active=True).count(),
            'total_fees_collected': school.payments.aggregate(total=Sum('amount'))['total'] or 0,
            'pending_fees': school.student_fees.filter(payment_status=PaymentStatusChoices.PENDING).aggregate(total=Sum('amount_due'))['total'] or 0,
            'overdue_fees': school.student_fees.filter(payment_status=PaymentStatusChoices.OVERDUE).aggregate(total=Sum('amount_due'))['total'] or 0,
        }
        return Response(stats)

class AcademicYearViewSet(BaseViewSet):
    """Academic Year ViewSet"""
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    search_fields = ['name']
    filterset_fields = ['is_current']
    
    @action(detail=True, methods=['post'])
    def set_current(self, request, pk=None):
        """Set as current academic year"""
        academic_year = self.get_object()
        # Reset all other years to not current
        AcademicYear.objects.filter(school=academic_year.school).update(is_current=False)
        # Set this year as current
        academic_year.is_current = True
        academic_year.save()
        return Response({'message': 'Academic year set as current'})

class ClassViewSet(BaseViewSet):
    """Class ViewSet"""
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    search_fields = ['name', 'grade', 'section']
    filterset_fields = ['grade', 'section']
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get students in this class"""
        class_obj = self.get_object()
        students = class_obj.students.filter(is_active=True)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def fee_summary(self, request, pk=None):
        """Get fee summary for this class"""
        class_obj = self.get_object()
        summary = {
            'total_students': class_obj.students.filter(is_active=True).count(),
            'total_fees_due': class_obj.students.filter(is_active=True).aggregate(
                total=Sum('fees__amount_due'))['total'] or 0,
            'total_fees_paid': class_obj.students.filter(is_active=True).aggregate(
                total=Sum('fees__amount_paid'))['total'] or 0,
        }
        return Response(summary)

class StudentViewSet(BaseViewSet):
    """Student ViewSet"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    search_fields = ['student_id', 'user__first_name', 'user__last_name', 'user__email']
    filterset_fields = ['current_class', 'status']
    
    @action(detail=True, methods=['get'])
    def fees(self, request, pk=None):
        """Get student fees"""
        student = self.get_object()
        fees = student.fees.all()
        serializer = StudentFeeSerializer(fees, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get student payments"""
        student = self.get_object()
        payments = student.payments.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def fee_summary(self, request, pk=None):
        """Get student fee summary"""
        student = self.get_object()
        summary = {
            'total_fees_due': student.fees.aggregate(total=Sum('amount_due'))['total'] or 0,
            'total_fees_paid': student.fees.aggregate(total=Sum('amount_paid'))['total'] or 0,
            'pending_fees': student.fees.filter(payment_status=PaymentStatusChoices.PENDING).count(),
            'overdue_fees': student.fees.filter(payment_status=PaymentStatusChoices.OVERDUE).count(),
        }
        return Response(summary)

class FeeStructureViewSet(BaseViewSet):
    """Fee Structure ViewSet"""
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    search_fields = ['fee_type', 'class_grade__name']
    filterset_fields = ['fee_type', 'class_grade', 'academic_year', 'is_mandatory']
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create fee structures for multiple classes"""
        data = request.data
        fee_structures = []
        
        for item in data.get('fee_structures', []):
            serializer = self.get_serializer(data=item)
            if serializer.is_valid():
                fee_structures.append(serializer.save())
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': f'{len(fee_structures)} fee structures created successfully',
            'created': len(fee_structures)
        })

class StudentFeeViewSet(BaseViewSet):
    """Student Fee ViewSet"""
    queryset = StudentFee.objects.all()
    serializer_class = StudentFeeSerializer
    search_fields = ['student__student_id', 'student__user__first_name', 'student__user__last_name']
    filterset_fields = ['payment_status', 'fee_structure__fee_type', 'student__current_class']
    
    @action(detail=False, methods=['get'])
    def pending_fees(self, request):
        """Get all pending fees"""
        pending_fees = self.get_queryset().filter(payment_status=PaymentStatusChoices.PENDING)
        serializer = self.get_serializer(pending_fees, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue_fees(self, request):
        """Get all overdue fees"""
        overdue_fees = self.get_queryset().filter(
            payment_status=PaymentStatusChoices.OVERDUE,
            due_date__lt=timezone.now().date()
        )
        serializer = self.get_serializer(overdue_fees, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def apply_discount(self, request, pk=None):
        """Apply discount to student fee"""
        student_fee = self.get_object()
        discount_amount = request.data.get('discount_amount', 0)
        
        if discount_amount > student_fee.amount_due:
            return Response({'error': 'Discount amount cannot exceed fee amount'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        student_fee.discount_amount = discount_amount
        student_fee.save()
        
        return Response({'message': 'Discount applied successfully'})

class PaymentViewSet(BaseViewSet):
    """Payment ViewSet"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    search_fields = ['receipt_number', 'student__student_id', 'student__user__first_name']
    filterset_fields = ['payment_method', 'payment_date', 'student__current_class']
    
    @action(detail=False, methods=['post'])
    def collect_payment(self, request):
        """Collect payment for student fees"""
        student_id = request.data.get('student_id')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        fee_allocations = request.data.get('fee_allocations', [])
        
        try:
            student = Student.objects.get(id=student_id, school=request.user.school)
            
            # Create payment record
            payment = Payment.objects.create(
                school=request.user.school,
                student=student,
                receipt_number=f"RCP{timezone.now().strftime('%Y%m%d')}{Payment.objects.count() + 1:04d}",
                payment_date=timezone.now(),
                amount=amount,
                payment_method=payment_method,
                collected_by=request.user
            )
            
            # Create payment details and update student fees
            for allocation in fee_allocations:
                student_fee = StudentFee.objects.get(id=allocation['student_fee_id'])
                allocation_amount = allocation['amount']
                
                PaymentDetail.objects.create(
                    payment=payment,
                    student_fee=student_fee,
                    amount=allocation_amount
                )
                
                student_fee.amount_paid += allocation_amount
                if student_fee.amount_paid >= student_fee.total_amount:
                    student_fee.payment_status = PaymentStatusChoices.PAID
                elif student_fee.amount_paid > 0:
                    student_fee.payment_status = PaymentStatusChoices.PARTIAL
                student_fee.save()
            
            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def receipt(self, request, pk=None):
        """Generate payment receipt"""
        payment = self.get_object()
        receipt_data = {
            'receipt_number': payment.receipt_number,
            'payment_date': payment.payment_date,
            'student_name': payment.student.user.get_full_name(),
            'student_id': payment.student.student_id,
            'amount': payment.amount,
            'payment_method': payment.get_payment_method_display(),
            'collected_by': payment.collected_by.get_full_name(),
            'payment_details': PaymentDetailSerializer(payment.payment_details.all(), many=True).data
        }
        return Response(receipt_data)
    
    @action(detail=False, methods=['get'])
    def daily_collection(self, request):
        """Get daily collection report"""
        date = request.query_params.get('date', timezone.now().date())
        payments = self.get_queryset().filter(payment_date__date=date)
        
        summary = {
            'date': date,
            'total_payments': payments.count(),
            'total_amount': payments.aggregate(total=Sum('amount'))['total'] or 0,
            'payment_methods': payments.values('payment_method').annotate(
                count=Count('id'),
                total=Sum('amount')
            ),
            'payments': PaymentSerializer(payments, many=True).data
        }
        return Response(summary)

class DiscountViewSet(BaseViewSet):
    """Discount ViewSet"""
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    search_fields = ['name', 'description']
    filterset_fields = ['discount_type', 'valid_from', 'valid_until']
    
    @action(detail=True, methods=['post'])
    def apply_to_student(self, request, pk=None):
        """Apply discount to a student"""
        discount = self.get_object()
        student_id = request.data.get('student_id')
        
        try:
            student = Student.objects.get(id=student_id, school=request.user.school)
            
            # Check if discount already applied
            if StudentDiscount.objects.filter(student=student, discount=discount).exists():
                return Response({'error': 'Discount already applied to this student'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Create student discount
            student_discount = StudentDiscount.objects.create(
                student=student,
                discount=discount,
                approved_by=request.user
            )
            
            return Response({'message': 'Discount applied successfully'})
            
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

class StudentDiscountViewSet(BaseViewSet):
    """Student Discount ViewSet"""
    queryset = StudentDiscount.objects.all()
    serializer_class = StudentDiscountSerializer
    search_fields = ['student__student_id', 'discount__name']
    filterset_fields = ['student', 'discount', 'approved_by']

# ================================
# fees/permissions.py
# ================================

from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):
    """Check if user is authenticated"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsSchoolOwnerOrReadOnly(BasePermission):
    """Check if user belongs to the same school"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'school')
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Check if object has school attribute
        if hasattr(obj, 'school'):
            return obj.school == request.user.school
        
        return True