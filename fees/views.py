from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from .models import *
from .forms import *

@login_required
def fees_dashboard(request):
    """Dashboard showing overview of fees"""
    total_students = Student.objects.filter(is_active=True).count()
    total_pending_payments = FeePayment.objects.filter(status='pending').count()
    total_overdue_payments = FeePayment.objects.filter(status='overdue').count()
    total_revenue = FeePayment.objects.filter(status='paid').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    recent_payments = FeePayment.objects.filter(status='paid').order_by('-payment_date')[:5]
    
    context = {
        'total_students': total_students,
        'total_pending_payments': total_pending_payments,
        'total_overdue_payments': total_overdue_payments,
        'total_revenue': total_revenue,
        'recent_payments': recent_payments,
    }
    return render(request, 'fees/dashboard.html', context)

@login_required
def student_list(request):
    """List all students with pagination and search"""
    query = request.GET.get('q', '')
    students = Student.objects.filter(is_active=True)
    
    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(student_id__icontains=query) |
            Q(email__icontains=query)
        )
    
    paginator = Paginator(students, 20)
    page = request.GET.get('page')
    students = paginator.get_page(page)
    
    return render(request, 'fees/student_list.html', {
        'students': students,
        'query': query
    })

@login_required
def student_detail(request, student_id):
    """Detailed view of a student's fee information"""
    student = get_object_or_404(Student, id=student_id)
    payments = FeePayment.objects.filter(student=student).order_by('-created_at')
    discounts = StudentDiscount.objects.filter(student=student, is_active=True)
    
    # Calculate totals
    total_due = payments.aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    total_paid = payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_pending = payments.filter(status='pending').aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    
    context = {
        'student': student,
        'payments': payments,
        'discounts': discounts,
        'total_due': total_due,
        'total_paid': total_paid,
        'total_pending': total_pending,
    }
    return render(request, 'fees/student_detail.html', context)

@login_required
def fee_structure_list(request):
    """List all fee structures"""
    structures = FeeStructure.objects.filter(is_active=True).select_related('category')
    return render(request, 'fees/fee_structure_list.html', {
        'structures': structures
    })

@login_required
def payment_list(request):
    """List all payments with filters"""
    status = request.GET.get('status', '')
    payments = FeePayment.objects.all().select_related('student', 'fee_structure')
    
    if status:
        payments = payments.filter(status=status)
    
    paginator = Paginator(payments, 25)
    page = request.GET.get('page')
    payments = paginator.get_page(page)
    
    return render(request, 'fees/payment_list.html', {
        'payments': payments,
        'status': status,
        'status_choices': FeePayment.PAYMENT_STATUS_CHOICES
    })

@login_required
def payment_detail(request, payment_id):
    """Detailed view of a payment"""
    payment = get_object_or_404(FeePayment, id=payment_id)
    return render(request, 'fees/payment_detail.html', {
        'payment': payment
    })

@login_required
def make_payment(request, payment_id):
    """Process a payment"""
    payment = get_object_or_404(FeePayment, id=payment_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payment_date = timezone.now().date()
            payment.status = 'paid'
            payment.save()
            messages.success(request, 'Payment processed successfully!')
            return redirect('fees:payment_detail', payment_id=payment.id)
    else:
        form = PaymentForm(instance=payment)
    
    return render(request, 'fees/make_payment.html', {
        'form': form,
        'payment': payment
    })

@login_required
def overdue_payments(request):
    """List overdue payments"""
    overdue_payments = FeePayment.objects.filter(
        status='pending',
        due_date__lt=timezone.now().date()
    ).select_related('student', 'fee_structure')
    
    # Update status to overdue
    overdue_payments.update(status='overdue')
    
    paginator = Paginator(overdue_payments, 25)
    page = request.GET.get('page')
    overdue_payments = paginator.get_page(page)
    
    return render(request, 'fees/overdue_payments.html', {
        'overdue_payments': overdue_payments
    })

@login_required
def fee_reports(request):
    """Generate fee reports"""
    # Monthly revenue
    monthly_revenue = FeePayment.objects.filter(
        status='paid',
        payment_date__month=timezone.now().month
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    # Payment statistics
    payment_stats = {
        'total_payments': FeePayment.objects.count(),
        'paid_payments': FeePayment.objects.filter(status='paid').count(),
        'pending_payments': FeePayment.objects.filter(status='pending').count(),
        'overdue_payments': FeePayment.objects.filter(status='overdue').count(),
    }
    
    return render(request, 'fees/reports.html', {
        'monthly_revenue': monthly_revenue,
        'payment_stats': payment_stats,
    })

# fees/forms.py
from django import forms
from .models import *

class PaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ['amount_paid', 'payment_method', 'transaction_id', 'notes']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'first_name', 'last_name', 'email', 'phone', 'address', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['category', 'name', 'amount', 'frequency', 'due_date', 'late_fee_amount', 'is_mandatory']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'late_fee_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }from django.shortcuts import render

# Create your views here.
