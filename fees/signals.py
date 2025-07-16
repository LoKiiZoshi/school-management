from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import *

@receiver(post_save, sender=Student)
def create_student_fees(sender, instance, created, **kwargs):
    """Create student fees when a new student is created"""
    if created:
        # Get current academic year
        try:
            current_year = AcademicYear.objects.get(
                school=instance.school, 
                is_current=True
            )
            
            # Get fee structures for the student's class
            fee_structures = FeeStructure.objects.filter(
                school=instance.school,
                academic_year=current_year,
                class_grade=instance.current_class
            )
            
            # Create student fees
            for fee_structure in fee_structures:
                StudentFee.objects.create(
                    school=instance.school,
                    student=instance,
                    fee_structure=fee_structure,
                    amount_due=fee_structure.amount,
                    due_date=fee_structure.due_date
                )
        except AcademicYear.DoesNotExist:
            pass

@receiver(pre_save, sender=StudentFee)
def update_payment_status(sender, instance, **kwargs):
    """Update payment status based on due date"""
    if instance.payment_status == PaymentStatusChoices.PENDING:
        if instance.due_date < timezone.now().date():
            instance.payment_status = PaymentStatusChoices.OVERDUE

@receiver(post_save, sender=Payment)
def update_student_fee_status(sender, instance, created, **kwargs):
    """Update student fee status after payment"""
    if created:
        # This is handled in the view, but we can add additional logic here
        pass