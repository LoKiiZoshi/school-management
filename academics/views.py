from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import *
from .serializers import *

# API ViewSets
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    def get_queryset(self):
        queryset = Student.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(student_id__icontains=search) |
                Q(roll_number__icontains=search)
            )
        return queryset

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_queryset(self):
        queryset = Book.objects.all()
        category = self.request.query_params.get('category', None)
        search = self.request.query_params.get('search', None)
        
        if category:
            queryset = queryset.filter(category=category)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(isbn__icontains=search)
            )
        return queryset
    
    @action(detail=True, methods=['post'])
    def issue_book(self, request, pk=None):
        book = self.get_object()
        student_id = request.data.get('student_id')
        
        if book.available_copies <= 0:
            return Response({'error': 'No copies available'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            student = Student.objects.get(student_id=student_id)
            # Check if student already has this book
            existing_issue = BookIssue.objects.filter(
                student=student, book=book, status='issued'
            ).first()
            
            if existing_issue:
                return Response({'error': 'Book already issued to this student'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create book issue
            from datetime import datetime, timedelta
            due_date = datetime.now() + timedelta(days=14)  # 2 weeks
            
            issue = BookIssue.objects.create(
                student=student,
                book=book,
                due_date=due_date
            )
            
            # Update available copies
            book.available_copies -= 1
            book.save()
            
            return Response(BookIssueSerializer(issue).data, status=status.HTTP_201_CREATED)
            
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

class BookIssueViewSet(viewsets.ModelViewSet):
    queryset = BookIssue.objects.all()
    serializer_class = BookIssueSerializer
    
    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        issue = self.get_object()
        
        if issue.status != 'issued':
            return Response({'error': 'Book not currently issued'}, status=status.HTTP_400_BAD_REQUEST)
        
        from datetime import datetime
        issue.return_date = datetime.now()
        issue.status = 'returned'
        
        # Calculate fine if overdue
        if issue.return_date.date() > issue.due_date.date():
            days_overdue = (issue.return_date.date() - issue.due_date.date()).days
            issue.fine_amount = days_overdue * 2.00  # $2 per day fine
        
        issue.save()
        
        # Update available copies
        issue.book.available_copies += 1
        issue.book.save()
        
        return Response(BookIssueSerializer(issue).data)

class FeeTypeViewSet(viewsets.ModelViewSet):
    queryset = FeeType.objects.all()
    serializer_class = FeeTypeSerializer

class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.all()
    serializer_class = FeePaymentSerializer
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        payment = self.get_object()
        amount = float(request.data.get('amount', 0))
        method = request.data.get('payment_method', 'cash')
        
        if amount <= 0:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        from datetime import datetime
        payment.amount_paid += amount
        payment.payment_method = method
        payment.payment_date = datetime.now()
        
        if payment.amount_paid >= payment.amount_due:
            payment.status = 'paid'
        else:
            payment.status = 'partial'
        
        payment.save()
        
        return Response(FeePaymentSerializer(payment).data)

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer

class TransportRegistrationViewSet(viewsets.ModelViewSet):
    queryset = TransportRegistration.objects.all()
    serializer_class = TransportRegistrationSerializer

class TransportPaymentViewSet(viewsets.ModelViewSet):
    queryset = TransportPayment.objects.all()
    serializer_class = TransportPaymentSerializer

# Web Views
@login_required
def dashboard(request):
    context = {
        'total_students': Student.objects.count(),
        'total_courses': Course.objects.count(),
        'total_books': Book.objects.count(),
        'pending_fees': FeePayment.objects.filter(status='pending').count(),
        'active_transports': TransportRegistration.objects.filter(status='active').count(),
    }
    return render(request, 'academic/dashboard.html', context)

@login_required
def student_list(request):
    students = Student.objects.all()
    search = request.GET.get('search', '')
    
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(student_id__icontains=search)
        )
    
    paginator = Paginator(students, 20)
    page = request.GET.get('page')
    students = paginator.get_page(page)
    
    context = {'students': students, 'search': search}
    return render(request, 'academic/student_list.html', context)

@login_required
def library_dashboard(request):
    context = {
        'total_books': Book.objects.count(),
        'issued_books': BookIssue.objects.filter(status='issued').count(),
        'overdue_books': BookIssue.objects.filter(status='overdue').count(),
        'available_books': Book.objects.filter(available_copies__gt=0).count(),
    }
    return render(request, 'academic/library_dashboard.html', context)

@login_required
def fee_dashboard(request):
    context = {
        'pending_payments': FeePayment.objects.filter(status='pending').count(),
        'overdue_payments': FeePayment.objects.filter(status='overdue').count(),
        'total_collected': FeePayment.objects.filter(status='paid').aggregate(
            total=models.Sum('amount_paid')
        )['total'] or 0,
    }
    return render(request, 'academic/fee_dashboard.html', context)

@login_required
def transport_dashboard(request):
    context = {
        'total_routes': Route.objects.count(),
        'total_buses': Bus.objects.filter(is_active=True).count(),
        'active_registrations': TransportRegistration.objects.filter(status='active').count(),
        'pending_payments': TransportPayment.objects.filter(status='pending').count(),
    }
    return render(request, 'academic/transport_dashboard.html', context)