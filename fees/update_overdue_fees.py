from django.core.management.base import BaseCommand
from django.utils import timezone
from fees.models import StudentFee, PaymentStatusChoices

class Command(BaseCommand):
    help = 'Update overdue fees status'
    
    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Update pending fees to overdue if past due date
        updated_count = StudentFee.objects.filter(
            payment_status=PaymentStatusChoices.PENDING,
            due_date__lt=today
        ).update(payment_status=PaymentStatusChoices.OVERDUE)
        
        self.stdout.write(
            self.style.SUCCESS(f'Updated {updated_count} fees to overdue status')
        )