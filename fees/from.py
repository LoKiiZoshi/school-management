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
        }